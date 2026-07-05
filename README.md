# Screencast Recorder

High-quality screencast recorder for Linux with a GTK4 GUI and CLI.

## Features

- Fullscreen, region, or per-window capture
- GTK4 graphical interface with recording timer
- CLI with hotkey toggle support (`--toggle`)
- Multiple quality presets: lossless, visually-lossless, high, medium
- Hardware-accelerated encoders (NVENC, VAAPI) when available
- Software encoders: H.264, H.265, FFV1
- Webcam picture-in-picture overlay
- Desktop audio + microphone recording
- Recording area border indicator
- Region selector with live screenshot preview
- Window picker with thumbnails

## Requirements

- Linux with X11
- Python 3.10+
- GTK 4, Libadwaita
- ffmpeg
- xdotool
- PulseAudio or PipeWire (for audio)
- xrandr (for monitor detection)

Optional:
- slop – interactive region selection from CLI
- notify-send (libnotify) – desktop notifications

## Install

### From pip

```bash
pip install .
```

### From source

```bash
git clone https://github.com/abraham/screencast-recorder.git
cd screencast-recorder
pip install .
```

## Usage

### GUI

```bash
screencast-recorder-gui
```

Bind `screencast-recorder-gui` to your preferred keyboard shortcut
(e.g. Ctrl+Shift+R in your DE settings).

### CLI

```bash
# Fullscreen monitor 0 (defaults)
screencast-recorder

# Select a region interactively (needs slop)
screencast-recorder --region

# Select a window (needs xdotool)
screencast-recorder --window

# Set geometry manually
screencast-recorder --geometry 800x600+100+200

# With microphone
screencast-recorder --audio-mic

# Hotkey toggle (bind to keyboard shortcut)
screencast-recorder --toggle
```

### Keyboard shortcuts (GUI)

| Key | Action |
|-----|--------|
| Ctrl+Enter | Start recording |
| Escape | Stop recording |
| Ctrl+P | Pause/resume |

## Quality Presets

| Preset | CRF | Audio | Use case |
|--------|-----|-------|----------|
| lossless | 0 | FLAC | Archival, editing |
| visually-lossless | 18 | Opus 320k | High quality |
| high | 16 | Opus 320k | Balanced |
| medium | 20 | Opus 320k | Smaller files |

## License

GNU General Public License v3.0 or later.
