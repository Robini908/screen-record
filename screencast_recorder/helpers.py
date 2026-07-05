import json, os, signal, subprocess

from .config import PID_FILE, CONFIG_FILE, STATUS_FILE


def fmt_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def notify(msg, timeout=3000):
    try:
        subprocess.Popen(
            ["notify-send", "-t", str(timeout), "Record", msg],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def save_config(data):
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


def is_recording():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            PID_FILE.unlink(missing_ok=True)
    return False


def stop_recording():
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        PID_FILE.unlink(missing_ok=True)
        return False


def update_status(pid=None, filepath=None, paused=False):
    data = {}
    if STATUS_FILE.exists():
        try:
            data = json.loads(STATUS_FILE.read_text())
        except Exception:
            pass
    if pid is not None:
        data["pid"] = pid
    if filepath is not None:
        data["filepath"] = str(filepath)
    if paused is not None:
        data["paused"] = paused
    STATUS_FILE.write_text(json.dumps(data))


def clear_status():
    for f in (STATUS_FILE, PID_FILE):
        try:
            f.unlink()
        except Exception:
            pass
