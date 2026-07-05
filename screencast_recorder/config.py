import os, subprocess
from pathlib import Path


def detect_display():
    d = os.environ.get("DISPLAY")
    if d:
        return d
    try:
        out = subprocess.check_output(["w"], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if ":" in line and " " in line:
                for part in line.split():
                    if part.startswith(":"):
                        return part
    except Exception:
        pass
    return ":0"


DISPLAY = detect_display()
os.environ["DISPLAY"] = DISPLAY

CACHE_DIR = Path.home() / ".cache" / "record"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE = CACHE_DIR / "record.pid"
CONFIG_FILE = CACHE_DIR / "config.json"
STATUS_FILE = CACHE_DIR / "status"

RECORDINGS_DIR = Path.home() / "Videos" / "Recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
