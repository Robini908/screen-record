import signal, subprocess, sys, time

from .config import DISPLAY, CACHE_DIR, RECORDINGS_DIR
from .cmd import build_command
from .helpers import fmt_size, notify, update_status, clear_status
from .region import border_window, destroy_border


RECORDING = False


def _handle_signal(signum, frame):
    global RECORDING
    RECORDING = False


def record(args):
    global RECORDING

    cmd, (x, y, w, h) = build_command(args)

    if not args.get("outfile"):
        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        ext = "mkv"
        args["outfile"] = RECORDINGS_DIR / f"screencast_{ts}.{ext}"

    outfile = args["outfile"]
    print(f"Output: {outfile}")
    print(f"Command: {' '.join(cmd[-10:])} ...")

    border = None
    if args.get("show_border"):
        border = border_window(x, y, w, h, DISPLAY)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
    )

    with open(CACHE_DIR / "pid", "w") as f:
        f.write(str(proc.pid))
    update_status(pid=proc.pid, filepath=str(outfile), paused=False)
    notify("Recording started", timeout=2000)

    global RECORDING
    RECORDING = True
    paused = False
    start_time = time.time()
    last_size = 0

    try:
        for line in proc.stdout:
            if not RECORDING:
                break

            if args.get("stdin_control") and sys.stdin.isatty():
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0)[0]:
                        user_input = sys.stdin.readline().strip().lower()
                        if user_input == "p":
                            paused = not paused
                            if paused:
                                proc.stdin.write(b"c")
                                proc.stdin.flush()
                                sys.stdout.write("\n⏸ PAUSED — press p to resume\n")
                            else:
                                proc.stdin.write(b"c")
                                proc.stdin.flush()
                                sys.stdout.write("\n▶ RESUMED\n")
                            update_status(paused=paused)
                        elif user_input == "q":
                            break
                except (ImportError, AttributeError):
                    pass

            if b"frame=" in line:
                elapsed = time.time() - start_time
                info = line.decode(errors="replace").strip()
                of = args["outfile"]
                if of.exists():
                    last_size = of.stat().st_size
                sys.stdout.write(
                    f"\r{info}  |  {fmt_size(last_size)}  |  "
                    f"{elapsed:.0f}s  |  {'⏸ PAUSED' if paused else '▶'}"
                )
                sys.stdout.flush()
    except (BrokenPipeError, OSError):
        pass

    print()
    destroy_border(border, DISPLAY)
    proc.stdin.close()
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    clear_status()

    elapsed = time.time() - start_time
    if outfile.exists():
        size = outfile.stat().st_size
        print(f"\nSaved: {outfile}")
        print(f"Size: {fmt_size(size)}, Duration: {elapsed:.0f}s")
        notify(f"Recording saved ({fmt_size(size)}, {elapsed:.0f}s)", timeout=5000)
    else:
        notify("Recording cancelled", timeout=3000)
