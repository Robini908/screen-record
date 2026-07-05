# Screencast Recorder

A high-quality screencast recorder for Linux (X11) with a GTK4 GUI and full-featured CLI. Records your screen, desktop audio, microphone, and webcam picture-in-picture into a single MKV file.

## Features

- **Three capture modes** — fullscreen, interactive region selection, or per-window capture
- **GTK4 / Libadwaita GUI** — clean settings panel, live recording timer with pause/resume
- **CLI with hotkey toggle** — bind `screencast-recorder --toggle` to a keyboard shortcut to start/stop without touching the mouse
- **Desktop audio + microphone** — records from your PulseAudio sink monitor (what you hear) plus optional mic, mixed in real time
- **Webcam overlay** — picture-in-picture at 320×240, positionable top-right or top-left
- **Hardware encoding** — auto-picks NVENC H.264 or VAAPI H.264 when available; falls back to software libx264
- **Recording border** — red translucent border marks the capture area while recording
- **Region selector** — drag-to-select overlay built right into the GUI
- **Window picker** — searchable list of open windows with dimensions
- **Modular design** — 18 small Python modules, each under 175 lines, easy to read and hack on

## Requirements

| Dependency | Purpose |
|---|---|
| Linux with X11 | X11 display server (x11grab) |
| Python ≥ 3.10 | Runtime |
| GTK 4 + Libadwaita | GUI toolkit |
| ffmpeg | Recording engine (video/audio capture + encoding) |
| xdotool | Window geometry detection |
| xrandr | Monitor list and resolution detection |
| PulseAudio or PipeWire | Desktop audio and microphone capture |

Optional:
- `slop` — interactive region selection from the `--region` CLI flag
- `notify-send` (libnotify) — desktop start/stop notifications

## Installation

### From pip (local checkout)

```bash
git clone https://github.com/Robini908/screen-record.git
cd screen-record
pip install .
```

### From source (editable, for development)

```bash
pip install -e .
```

### Using pipx (recommended for isolation)

```bash
pipx install .
```

After installation two commands are available:

- `screencast-recorder` — CLI interface
- `screencast-recorder-gui` — graphical interface

## Usage

### GUI

```bash
screencast-recorder-gui
```

Opens a settings window where you pick capture mode, encoder, audio sources, and webcam. Click **Start Recording** — the window switches to a timer view with Pause and Stop buttons.

Bind it to a keyboard shortcut in your DE settings (e.g. Ctrl+Shift+R):

```bash
screencast-recorder-gui
```

### CLI fullscreen

```bash
screencast-recorder
```

Records the primary monitor at 60 FPS with libx264, CRF 18. Press `p` to pause, `q` to quit.

### CLI with options

```bash
# Record a specific monitor (0-based index from --list-monitors)
screencast-recorder --monitor 0

# Interactive region selection (requires slop)
screencast-recorder --region

# Select window by title substring
screencast-recorder --window "Firefox"

# Set geometry manually: x y w h
screencast-recorder --geometry "100 200 1920 1080"

# Change frame rate and encoder
screencast-recorder --fps 30 --vcodec libx265

# With desktop audio + microphone
screencast-recorder --list-mics        # list available mic sources
screencast-recorder --mic "alsa_input..."

# No audio at all
screencast-recorder --no-audio

# With webcam overlay
screencast-recorder --webcam video0

# Specific output file
screencast-recorder --outfile ~/Videos/my-recording.mkv
```

### Hotkey toggle

Bind this to a keyboard shortcut to start/stop recording silently:

```bash
screencast-recorder --toggle
```

The first press starts recording using the last-used settings (stored in `~/.cache/record/config.json`). The second press stops it.

### Utility commands

```bash
screencast-recorder --list-monitors   # show connected displays
screencast-recorder --list-encoders   # test all available encoders
screencast-recorder --list-mics       # show microphone sources
screencast-recorder --list-webcams    # show /dev/video* devices
```

## CLI reference

```
usage: screencast-recorder [-h] [--list-monitors] [--list-encoders] [--toggle]
                           [--region] [--monitor MONITOR] [--window WINDOW]
                           [--geometry GEOMETRY] [--fps FPS] [--vcodec VCODEC]
                           [--mic MIC] [--list-mics] [--no-audio]
                           [--webcam WEBCAM] [--list-webcams] [--no-sound]
                           [--outfile OUTFILE] [--nvidia-gpu] [--greedy]
```

| Flag | Description |
|---|---|
| `--list-monitors` | List detected monitors and exit |
| `--list-encoders` | Test all video encoders and exit |
| `--toggle` | Start recording or stop if already running |
| `--region` | Select a screen region interactively (needs slop/xrectsel) |
| `--monitor N` | Capture monitor index N (0-based) |
| `--window TITLE` | Capture a window by title substring |
| `--geometry "x y w h"` | Capture area as `"left top width height"` |
| `--fps N` | Frame rate (default 60) |
| `--vcodec CODEC` | Video codec (default libx264) |
| `--mic NAME` | Microphone source name |
| `--no-audio` / `--no-sound` | Disable all audio capture |
| `--webcam DEV` | Webcam device name (e.g. video0) |
| `--list-mics` | List microphone sources and exit |
| `--list-webcams` | List webcam devices and exit |
| `--outfile PATH` | Output file path (default `~/Videos/Recordings/screencast_*.mkv`) |
| `--nvidia-gpu` / `--greedy` | Enable CUDA hardware acceleration |

## Output

Recordings are saved to `~/Videos/Recordings/screencast_YYYY-MM-DD_HH-MM-SS.mkv` by default.

Audio codec: PCM 16-bit 48 kHz (lossless, compatible with every editor).

## Project structure

```
screencast_recorder/
├── config.py              — DISPLAY, cache dirs, constants
├── display.py             — xrandr monitor detection
├── region.py              — interactive region selection, border window
├── encoders.py            — encoder detection and parameter generation
├── audio.py               — PulseAudio sink monitor and mic discovery
├── windows.py             — xdotool window listing
├── webcam.py              — /dev/video* device scan
├── helpers.py             — notifications, config persistence, PID tracking
├── cmd.py                 — ffmpeg command-line builder
├── recorder.py            — CLI recording loop (stdin control, progress)
├── cli.py                 — argument parser and CLI entry point
├── gui.py                 — GTK application class
├── gui_window.py          — main recording window
├── gui_settings.py        — settings / preferences page
├── gui_recording.py       — recording controller and recording page
├── gui_region_picker.py   — drag-to-select region overlay
└── gui_window_picker.py   — searchable window list dialog
```

## License

GNU General Public License v3.0 or later.
