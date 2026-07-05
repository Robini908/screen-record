import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from .display import get_monitors
from .audio import mic_sources
from .webcam import webcam_sources


def _hbox():
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)


def _make_section(title, widget, subtitle=None):
    group = Adw.PreferencesGroup()
    group.set_title(title)
    if subtitle:
        group.set_description(subtitle)
    row = Adw.ActionRow()
    row.add_suffix(widget)
    row.set_activatable_widget(widget)
    group.add(row)
    return group


def _on_mode_changed(window, combo):
    mode = combo.get_active().lower()
    window.config["mode"] = mode
    if mode == "fullscreen":
        monitor = get_monitors()
        if monitor:
            _, w, h, x, y = monitor[0]
            window.config["geometry"] = f"{x} {y} {w} {h}"
    window.config.pop("window_id", None)
    window.config.pop("window_name", None)


def build_settings_page(window):
    page = Adw.PreferencesPage()
    page.set_margin_top(16)
    page.set_margin_bottom(16)
    page.set_margin_start(12)
    page.set_margin_end(12)

    mode_combo = Gtk.ComboBoxText()
    for m in ("Fullscreen", "Region", "Window"):
        mode_combo.append_text(m)
    mode_combo.set_active(
        {"fullscreen": 0, "region": 1, "window": 2}.get(
            window.config.get("mode", "fullscreen"), 0
        )
    )
    mode_combo.connect("changed", lambda c: _on_mode_changed(window, c))
    page.add(_make_section("Capture Mode", mode_combo,
                           "Screen, region, or specific window"))

    if window.config.get("mode") == "window":
        win_btn = Gtk.Button(label="Select Window")
        win_btn.connect("clicked", lambda b: _pick_window(window))
        page.add(_make_section("Window", win_btn))
    elif window.config.get("mode") == "region":
        region_btn = Gtk.Button(label="Select Region")
        region_btn.connect("clicked", lambda b: _pick_region(window))
        page.add(_make_section("Region", region_btn))

    fps_spin = Gtk.SpinButton.new_with_range(1, 120, 1)
    fps_spin.set_value(window.config.get("fps", 60))
    fps_spin.connect("value-changed", lambda s: window.config.update(
        fps=int(s.get_value())))
    page.add(_make_section("FPS", fps_spin))

    enc_combo = Gtk.ComboBoxText()
    enc_combo.append_text("Auto")
    encoders = ["libx264", "h264_nvenc", "h264_vaapi", "libx265", "hevc_nvenc"]
    for e in encoders:
        enc_combo.append_text(e)
    current = window.config.get("vcodec", "")
    all_encoders = [""] + encoders
    enc_combo.set_active(all_encoders.index(current) if current in all_encoders else 0)
    enc_combo.connect("changed", lambda c: window.config.update(
        vcodec=c.get_active_text() if c.get_active() > 0 else ""))
    page.add(_make_section("Encoder", enc_combo, "Select video codec"))

    audio_group = Adw.PreferencesGroup()
    audio_group.set_title("Audio")
    page.add(audio_group)

    desk_row = Adw.ActionRow(title="Desktop Audio")
    desk_switch = Gtk.Switch()
    desk_switch.set_active(bool(window.config.get("desktop_audio")))
    desk_row.add_suffix(desk_switch)
    desk_row.set_activatable_widget(desk_switch)
    audio_group.add(desk_row)

    mic_row = Adw.ActionRow(title="Microphone")
    mic_switch = Gtk.Switch()
    mic_switch.set_active(bool(window.config.get("mic")))
    mic_row.add_suffix(mic_switch)
    mic_row.set_activatable_widget(mic_switch)
    audio_group.add(mic_row)

    def on_audio_toggled(*a):
        from .audio import default_audio_src
        if desk_switch.get_active():
            src = default_audio_src()
            if src:
                window.config["desktop_audio"] = src
        else:
            window.config.pop("desktop_audio", None)
        if mic_switch.get_active():
            mics = mic_sources()
            if mics:
                window.config["mic"] = mics[0]["name"]
        else:
            window.config.pop("mic", None)
    desk_switch.connect("notify::active", on_audio_toggled)
    mic_switch.connect("notify::active", on_audio_toggled)

    webcam_group = Adw.PreferencesGroup()
    webcam_group.set_title("Webcam Overlay")
    page.add(webcam_group)

    webcam_combo = Gtk.ComboBoxText()
    webcam_combo.append_text("None")
    for dev, label in webcam_sources():
        webcam_combo.append_text(dev)
    webcam_combo.set_active(0)
    webcam_combo.connect("changed", lambda c: window.config.update(
        webcam=c.get_active_text() if c.get_active() > 0 else ""))
    webcam_row = Adw.ActionRow(title="Webcam")
    webcam_row.add_suffix(webcam_combo)
    webcam_row.set_activatable_widget(webcam_combo)
    webcam_group.add(webcam_row)

    start_btn = Gtk.Button(label="Start Recording",
                           halign=Gtk.Align.CENTER,
                           css_classes=["suggested-action", "pill"])
    start_btn.set_margin_top(16)
    start_btn.set_margin_bottom(16)
    start_btn.connect("clicked", lambda b: window._on_start())
    window.settings_box.append(start_btn)

    window.settings_box.append(page)


def _pick_window(window):
    from .gui_window_picker import WindowPicker
    picker = WindowPicker(window)
    picker.present()


def _pick_region(window):
    from .gui_region_picker import RegionSelector
    rs = RegionSelector(window)
    rs.present()
