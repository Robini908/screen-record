import subprocess, threading, time

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from .config import CACHE_DIR, RECORDINGS_DIR, DISPLAY
from .cmd import build_command
from .helpers import fmt_size, notify, update_status, clear_status
from .region import border_window, destroy_border


class RecordingController:
    def __init__(self):
        self.proc = None
        self.border = None
        self.ffmpeg_thread = None
        self.paused = False
        self.start_time = 0
        self.started = False
        self.elapsed = 0
        self.outfile = None
        self.geometry = None
        self.tick_id = None

    def start(self, window):
        geometry = window.config.get("geometry", "0 0 1920 1080")
        self.geometry = geometry

        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        ext = "mkv"
        self.outfile = RECORDINGS_DIR / f"screencast_{ts}.{ext}"

        args = {
            "vcodec": window.config.get("vcodec", "libx264"),
            "fps": window.config.get("fps", 60),
            "geometry": geometry,
            "desktop_audio": window.config.get("desktop_audio", ""),
            "mic": window.config.get("mic", ""),
            "webcam": window.config.get("webcam", ""),
            "nvidia_gpu": window.config.get("nvidia_gpu", False),
            "show_border": False,
            "outfile": self.outfile,
        }
        cmd, (x, y, w, h) = build_command(args)

        self.proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
        )

        self.border = border_window(x, y, w, h, DISPLAY)

        with open(CACHE_DIR / "pid", "w") as f:
            f.write(str(self.proc.pid))
        update_status(pid=self.proc.pid, filepath=str(self.outfile), paused=False)

        self.start_time = time.time()
        self.started = True
        self.paused = False
        self.last_size = 0
        self.elapsed = 0

        self.ffmpeg_thread = threading.Thread(
            target=self._read_output, daemon=True
        )
        self.ffmpeg_thread.start()

        build_recording_page(window)
        notify("Recording started", timeout=2000)

    def _read_output(self):
        for line in self.proc.stdout:
            if b"frame=" in line:
                self.last_line = line.decode(errors="replace").strip()
                if self.outfile.exists():
                    self.last_size = self.outfile.stat().st_size

    def stop(self, window):
        self.started = False
        if self.tick_id:
            GLib.source_remove(self.tick_id)
            self.tick_id = None
        destroy_border(self.border, DISPLAY)
        if self.proc:
            self.proc.stdin.close()
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self._show_result(window)

    def toggle_pause(self, window):
        if not self.proc:
            return
        self.paused = not self.paused
        self.proc.stdin.write(b"c" if self.paused else b"c")
        self.proc.stdin.flush()
        update_status(paused=self.paused)
        self._update_pause_label(window)

    def _update_pause_label(self, window):
        if hasattr(window, "pause_btn"):
            window.pause_btn.set_label("Resume" if self.paused else "Pause")

    def _show_result(self, window):
        clear_status()
        elapsed = time.time() - self.start_time
        if self.outfile and self.outfile.exists():
            size = self.outfile.stat().st_size
            notify(f"Recording saved ({fmt_size(size)}, {elapsed:.0f}s)", timeout=5000)
        window.close()

    def tick(self, window):
        elapsed = time.time() - self.start_time
        self.elapsed = int(elapsed)
        hours, rem = divmod(self.elapsed, 3600)
        mins, secs = divmod(rem, 60)
        ts = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

        if hasattr(window, "timer_label"):
            window.timer_label.set_text(f"{'⏸ ' if self.paused else ''}{ts}")
        if hasattr(window, "size_label"):
            window.size_label.set_text(fmt_size(self.last_size) if self.last_size else "")

        return self.started


def build_recording_page(window):
    for child in list(window.recording_box):
        window.recording_box.remove(child)

    overlay = Adw.ToastOverlay()
    window.toast_overlay = overlay
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_valign(Gtk.Align.CENTER)
    box.set_halign(Gtk.Align.CENTER)

    timer = Gtk.Label(css_classes=["recording-label"])
    timer.set_text("00:00")
    window.timer_label = timer
    box.append(timer)

    size_lbl = Gtk.Label()
    size_lbl.set_margin_bottom(16)
    size_lbl.set_css_classes(["dim-label"])
    window.size_label = size_lbl
    box.append(size_lbl)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12,
                      halign=Gtk.Align.CENTER)
    btn_box.set_homogeneous(True)

    pause_btn = Gtk.Button(label="Pause", css_classes=["pill"])
    pause_btn.connect("clicked", lambda b: window._on_pause())
    window.pause_btn = pause_btn
    btn_box.append(pause_btn)

    stop_btn = Gtk.Button(label="Stop", css_classes=["destructive-action", "pill"])
    stop_btn.connect("clicked", lambda b: window._on_stop())
    btn_box.append(stop_btn)

    box.append(btn_box)
    overlay.set_child(box)
    window.recording_box.append(overlay)
    window.stack.set_visible_child(window.recording_box)

    window.controller.tick_id = GLib.timeout_add(
        500, window.controller.tick, window
    )
