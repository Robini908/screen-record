import subprocess


def list_windows():
    try:
        out = subprocess.check_output(
            ["xdotool", "search", "--onlyvisible", "--name", "."],
            text=True, timeout=5,
        )
    except Exception:
        return []
    windows = []
    for wid in out.strip().splitlines():
        wid = wid.strip()
        if not wid:
            continue
        try:
            name = subprocess.check_output(
                ["xdotool", "getwindowname", wid],
                text=True, timeout=2, stderr=subprocess.DEVNULL,
            ).strip()
            geom = subprocess.check_output(
                ["xdotool", "getwindowgeometry", wid],
                text=True, timeout=2, stderr=subprocess.DEVNULL,
            )
            x = y = w = h = 0
            for gline in geom.splitlines():
                if gline.startswith("  Position:"):
                    _, rest = gline.split(":", 1)
                    xs, ys = rest.split(",")
                    x, y = int(xs.strip().lstrip(" ")), int(ys.strip().lstrip(" "))
                if gline.startswith("  Geometry:"):
                    _, rest = gline.split(":", 1)
                    ws, hs = rest.split("x")
                    w, h = int(ws.strip()), int(hs.strip())
        except Exception:
            continue
        windows.append({"id": wid, "name": name, "x": x, "y": y, "w": w, "h": h})
    return windows
