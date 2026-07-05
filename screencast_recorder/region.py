import subprocess, sys


def select_geometry(display):
    try:
        proc = subprocess.Popen(
            ["slop"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"DISPLAY": display},
        )
        out, _ = proc.communicate(timeout=30)
        x, y, w, h = map(int, out.decode().strip().split())
        return x, y, w, h
    except Exception:
        pass
    try:
        proc = subprocess.Popen(
            ["xrectsel"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"DISPLAY": display},
        )
        out, _ = proc.communicate(timeout=30)
        parts = out.decode().strip().split()
        return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    except Exception:
        raise RuntimeError(
            "Install slop or xrectsel for region selection:\n"
            "  sudo apt install slop\n"
            "  sudo apt install xrectsel"
        )


def border_window(x, y, w, h, display):
    code = f"""
import tkinter as tk
r = tk.Tk()
r.overrideredirect(True)
r.geometry("{w}x{h}+{x}+{y}")
r.attributes("-topmost", True)
r.configure(bg="red")
r.attributes("-alpha", 0.3)
r.bind("<Button-1>", lambda e: r.destroy())
r.mainloop()
"""
    return subprocess.Popen(
        [sys.executable, "-c", code],
        env={"DISPLAY": display},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def destroy_border(proc, display):
    if proc is None or proc.poll() is not None:
        return
    try:
        out = subprocess.check_output(
            ["xdotool", "search", "--name", "tk"],
            env={"DISPLAY": display}, timeout=2, text=True,
        )
        for wid in out.strip().split():
            subprocess.run(
                ["xdotool", "windowkill", wid],
                env={"DISPLAY": display}, timeout=2,
            )
    except Exception:
        proc.kill()
    try:
        proc.wait(timeout=3)
    except Exception:
        pass
