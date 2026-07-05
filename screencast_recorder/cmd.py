from .config import DISPLAY
from .encoders import encoder_params


def build_command(args):
    vcodec = args.get("vcodec", "libx264")
    vp, ap, aop = encoder_params(vcodec)
    cmd = ["ffmpeg", "-hide_banner"]

    if args.get("nvidia_gpu"):
        cmd += ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]

    geometry = args.get("geometry", "")
    x, y, w, h = 0, 0, 0, 0
    if geometry:
        parts = geometry.split()
        if len(parts) == 4:
            x, y, w, h = map(int, parts)
            cmd += [
                "-video_size", f"{w}x{h}",
                "-framerate", str(args.get("fps", 60)),
                "-f", "x11grab",
                "-thread_queue_size", "128",
                "-probesize", "10M",
                "-draw_mouse", "1",
                "-i", f"{DISPLAY}+{x},{y}",
            ]
    else:
        cmd += [
            "-video_size", "1920x1080",
            "-framerate", str(args.get("fps", 60)),
            "-f", "x11grab",
            "-thread_queue_size", "128",
            "-probesize", "10M",
            "-draw_mouse", "1",
            "-i", DISPLAY,
        ]

    mic = args.get("mic", "")
    desktop_audio = args.get("desktop_audio", "")

    if desktop_audio and mic:
        cmd += [
            "-f", "pulse",
            "-thread_queue_size", "128",
            "-i", desktop_audio,
            "-f", "pulse",
            "-thread_queue_size", "128",
            "-i", mic,
        ]
        cmd += ["-filter_complex",
                f"[0:a]{'volume=1.5' if args.get('boost_desktop') else 'volume=1'}[desk];"
                f"[1:a]{'volume=2.0' if args.get('boost_mic') else 'volume=1'}[mic];"
                "[desk][mic]amix=inputs=2:duration=first[aout]",
                "-map", "[aout]"]
        cmd += aop
    elif desktop_audio:
        cmd += [
            "-f", "pulse",
            "-thread_queue_size", "128",
            "-i", desktop_audio,
        ]
        cmd += ap
    elif mic:
        cmd += [
            "-f", "pulse",
            "-thread_queue_size", "128",
            "-i", mic,
        ]
        cmd += aop
    else:
        cmd += ["-an"]

    webcam = args.get("webcam", "")
    if webcam:
        cmd += [
            "-f", "v4l2",
            "-thread_queue_size", "64",
            "-video_size", "320x240",
            "-framerate", "15",
            "-i", f"/dev/{webcam}",
        ]
        if args.get("pip_position", "top-right") == "top-right":
            pos = "main_w-overlay_w-10:10"
        else:
            pos = "10:10"
        cmd += [
            "-filter_complex",
            f"[0:v]setpts=PTS[bg];[2:v]setpts=PTS,scale=320:-1[fg];"
            f"[bg][fg]overlay={pos}:format=auto[out]",
            "-map", "[out]",
        ]

    cmd += vp

    if args.get("outfile"):
        cmd += ["-y", args["outfile"]]

    return cmd, (x, y, w, h)
