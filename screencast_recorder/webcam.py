from pathlib import Path


def webcam_sources():
    sources = []
    for dev in Path("/dev").glob("video*"):
        try:
            path = Path("/sys/class/video4linux") / dev.name
            if not path.exists():
                sources.append((dev.name, dev.name))
                continue
            name_file = path / "name"
            if name_file.exists():
                label = name_file.read_text().strip()
            else:
                label = dev.name
            sources.append((dev.name, label))
        except Exception:
            sources.append((dev.name, dev.name))
    return sources
