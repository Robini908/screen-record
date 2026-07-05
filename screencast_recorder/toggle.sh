#!/usr/bin/env bash
# toggle.sh — keyboard shortcut companion: starts/stops recording silently.
# Bind this to a global hotkey in your WM/DE settings.

exec >/dev/null 2>&1

if ! command -v screencast-recorder &>/dev/null; then
    notify-send "Screen Recorder" "screencast-recorder: command not found"
    exit 1
fi

screencast-recorder --toggle
