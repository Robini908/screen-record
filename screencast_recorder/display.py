import re, subprocess


def get_monitors():
    try:
        out = subprocess.check_output(["xrandr", "--current"], text=True)
    except FileNotFoundError:
        return []
    monitors = []
    for line in out.splitlines():
        m = re.match(
            r'^(\S+)\s+connected\s+(?:primary\s+)?(\d+)x(\d+)\+(\d+)\+(\d+)', line
        )
        if m:
            monitors.append(
                (m.group(1), int(m.group(2)), int(m.group(3)),
                 int(m.group(4)), int(m.group(5)))
            )
    return monitors


def list_monitors():
    monitors = get_monitors()
    if not monitors:
        print("No monitors detected via xrandr.")
        return
    print(f"{'#':>3}  {'Name':<12}  {'Resolution':>12}  {'Offset':>10}")
    print("━" * 44)
    for i, (name, w, h, x, y) in enumerate(monitors):
        print(f"{i:>3}  {name:<12}  {w:>4}x{h:<4}  {x:+}{y:+}")


def list_encoders():
    candidates = {
        "av1_nvenc": "NVIDIA NVENC AV1 (hw)",
        "hevc_nvenc": "NVIDIA NVENC H.265 (hw)",
        "h264_nvenc": "NVIDIA NVENC H.264 (hw)",
        "hevc_vaapi": "VAAPI H.265 (hw)",
        "h264_vaapi": "VAAPI H.264 (hw)",
        "libx265": "libx265 H.265 (sw)",
        "libx264": "libx264 H.264 (sw)",
        "ffv1": "FFV1 lossless (sw)",
    }
    test_probe = ["-f", "lavfi", "-i", "color=s=320x240:d=0.1", "-pix_fmt", "yuv420p"]
    print(f"{'Encoder':<18}  {'Status':>8}  {'Description'}")
    print("━" * 52)
    for e, desc in candidates.items():
        r = subprocess.run(
            ["ffmpeg", "-hide_banner"] + test_probe + ["-c:v", e, "-f", "null", "-"],
            capture_output=True, timeout=5,
        )
        status = "✓" if r.returncode == 0 else "✗"
        print(f"{e:<18}  {status:>8}  {desc}")
