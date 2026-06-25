# Focus Timer

A Pomodoro-style focus timer for the terminal.

## Features

- 25-minute focus sessions with 5-minute short breaks and 15-minute long breaks
- Progress bar and countdown display
- macOS desktop notifications when sessions end
- Session history logged to `sessions.json` — shows the last 7 days on startup

## Usage

```bash
python3 timer.py
```

You'll be prompted for what you're working on, then the timer starts. Press `Ctrl+C` at any time to stop early.

## Requirements

- Python 3
- macOS (for desktop notifications via `osascript`)
