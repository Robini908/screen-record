import re, subprocess


def default_audio_src():
    try:
        out = subprocess.check_output(
            ["pactl", "info"], text=True, timeout=3
        )
        sink = None
        for line in out.splitlines():
            m = re.match(r"Default Sink:\s*(.+)", line)
            if m:
                sink = m.group(1).strip()
                break
        if not sink:
            return ""
        out2 = subprocess.check_output(
            ["pactl", "list", "sinks"], text=True, timeout=3
        )
        in_sink = False
        for line in out2.splitlines():
            if f"Name: {sink}" in line:
                in_sink = True
            if in_sink and "Monitor Source:" in line:
                return line.split(":", 1)[1].strip()
        return sink + ".monitor"
    except Exception:
        return ""


def mic_sources():
    try:
        out = subprocess.check_output(
            ["pactl", "list", "sources"], text=True, timeout=3
        )
    except Exception:
        return []
    sources, current = [], {}
    for line in out.splitlines():
        if line.startswith("Source #"):
            if current:
                sources.append(current)
            current = {"name": "", "desc": "", "monitor": False}
        if "Name:" in line and current is not None:
            current["name"] = line.split(":", 1)[1].strip()
        if "Description:" in line and current is not None:
            current["desc"] = line.split(":", 1)[1].strip()
        if "Monitor of Sink:" in line and current is not None:
            if line.split(":", 1)[1].strip():
                current["monitor"] = True
    if current:
        sources.append(current)
    return [s for s in sources if not s.get("monitor")]
