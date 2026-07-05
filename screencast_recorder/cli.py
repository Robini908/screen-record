import argparse

from .config import DISPLAY
from .helpers import load_config, is_recording, stop_recording
from .display import list_monitors, list_encoders
from .audio import mic_sources
from .webcam import webcam_sources
from .recorder import record


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="screencast-recorder")
    p.add_argument("--list-monitors", action="store_true", help="list monitors")
    p.add_argument("--list-encoders", action="store_true", help="list encoders")
    p.add_argument("--toggle", action="store_true", help="start/stop recording")
    p.add_argument("--region", action="store_true", help="select region with slop")
    p.add_argument("--monitor", type=int, help="monitor index (0-based)")
    p.add_argument("--window", type=str, help="window title substring")
    p.add_argument("--geometry", type=str, help="x y w h")
    p.add_argument("--fps", type=int, default=60, help="frames per second")
    p.add_argument("--vcodec", type=str, default="libx264", help="video codec")
    p.add_argument("--mic", type=str, default="", help="mic source name")
    p.add_argument("--list-mics", action="store_true", help="list mic sources")
    p.add_argument("--no-audio", action="store_true", help="disable audio")
    p.add_argument("--webcam", type=str, default="", help="webcam device name")
    p.add_argument("--list-webcams", action="store_true", help="list webcams")
    p.add_argument("--no-sound", action="store_true", help="alias for --no-audio")
    p.add_argument("--outfile", type=str, help="output file path")
    p.add_argument("--nvidia-gpu", action="store_true", help="nvidia GPU acceleration")
    p.add_argument("--greedy", action="store_true", help="GPU encoding alias")
    return p.parse_args(argv)


def main():
    args = parse_args()

    if args.list_monitors:
        list_monitors()
        return

    if args.list_encoders:
        list_encoders()
        return

    if args.list_mics:
        for m in mic_sources():
            print(f"{m['name']:30}  {m['desc']}")
        return

    if args.list_webcams:
        for dev, label in webcam_sources():
            print(f"{dev:10}  {label}")
        return

    if args.toggle:
        if is_recording():
            if stop_recording():
                print("Stopped recording.")
            else:
                print("Failed to stop recording.")
        else:
            start_from_toggle(args)
        return

    start_recording(args)


def _resolve_geometry(args):
    if args.region:
        from .region import select_geometry
        x, y, w, h = select_geometry(DISPLAY)
        return f"{x} {y} {w} {h}"

    if args.monitor is not None:
        from .display import get_monitors
        monitors = get_monitors()
        if args.monitor < len(monitors):
            _, w, h, x, y = monitors[args.monitor]
            return f"{x} {y} {w} {h}"

    if args.window:
        from .windows import list_windows
        for w in list_windows():
            if args.window.lower() in w["name"].lower():
                return f"{w['x']} {w['y']} {w['w']} {w['h']}"

    if args.geometry:
        return args.geometry

    config = load_config()
    saved = config.get("geometry", "")
    if saved:
        return saved
    return ""


def start_from_toggle(args):
    config = load_config()
    geometry = config.get("geometry", "")
    if geometry:
        args.geometry = geometry
    start_recording(args)


def start_recording(args):
    geometry = _resolve_geometry(args)
    if not geometry and not args.region and args.monitor is None:
        geometry = "0 0 1920 1080"

    if args.no_audio or args.no_sound:
        desktop_audio = ""
        mic = ""
    else:
        config = load_config()
        desktop_audio = config.get("desktop_audio", "")
        mic = args.mic or config.get("mic", "")

    record_params = {
        "vcodec": args.vcodec,
        "fps": args.fps,
        "geometry": geometry,
        "desktop_audio": desktop_audio,
        "mic": mic,
        "webcam": args.webcam,
        "nvidia_gpu": args.nvidia_gpu or args.greedy,
        "show_border": True,
        "stdin_control": True,
        "outfile": args.outfile,
    }
    record(record_params)


if __name__ == "__main__":
    main()
