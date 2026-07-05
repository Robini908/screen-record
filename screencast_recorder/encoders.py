import subprocess

_TEST_PROBE = ["-f", "lavfi", "-i", "color=s=320x240:d=0.1", "-pix_fmt", "yuv420p"]


def _check_encoder(name):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner"] + _TEST_PROBE + ["-c:v", name, "-f", "null", "-"],
        capture_output=True, timeout=8,
    )
    return r.returncode == 0


def best_encoder():
    for enc in ["libx264", "h264_nvenc", "h264_vaapi", "libx265", "hevc_nvenc"]:
        if _check_encoder(enc):
            return enc
    return "libx264"


def encoder_params(codec):
    if codec in ("libx264", "h264_vaapi"):
        v = ["-c:v", codec, "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"]
    elif codec == "h264_nvenc":
        v = ["-c:v", codec, "-preset", "p4", "-rc", "vbr", "-cq", "21", "-pix_fmt", "yuv420p"]
    elif codec == "libx265":
        v = ["-c:v", codec, "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p"]
    elif codec == "hevc_nvenc":
        v = ["-c:v", codec, "-preset", "p4", "-rc", "vbr", "-cq", "23", "-pix_fmt", "yuv420p"]
    else:
        v = ["-c:v", codec, "-pix_fmt", "yuv420p"]

    a = ["-c:a", "pcm_s16le", "-ar", "48000"]
    ao = ["-c:a", "pcm_s16le", "-ar", "48000"]
    return v, a, ao
