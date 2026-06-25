#!/usr/bin/env python3
import time
import sys
import os
import json
import signal
from datetime import date

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
POMODOROS_BEFORE_LONG = 4

COLORS = {
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "blue":   "\033[94m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}

def c(color, text):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def clear():
    os.system("clear")

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE) as f:
            return json.load(f)
    return {}

def save_session(sessions):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

def log_completed(label):
    sessions = load_sessions()
    today = str(date.today())
    sessions.setdefault(today, []).append({"label": label, "completed_at": time.strftime("%H:%M")})
    save_session(sessions)

def notify(title, msg):
    # macOS notification
    os.system(f'osascript -e \'display notification "{msg}" with title "{title}" sound name "Glass"\'')

def progress_bar(elapsed, total, width=40):
    pct = elapsed / total
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar

def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def run_timer(label, duration_min, color):
    total = duration_min * 60
    start = time.time()

    def handle_interrupt(sig, frame):
        clear()
        print(c("yellow", f"\n  Timer stopped early.\n"))
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_interrupt)

    while True:
        elapsed = time.time() - start
        remaining = total - elapsed
        if remaining <= 0:
            break

        clear()
        pct = int((elapsed / total) * 100)
        bar = progress_bar(elapsed, total)

        print()
        print(c("bold", f"  {'🍅 FOCUS' if color == 'red' else '☕ BREAK'}  —  {label}"))
        print()
        print(f"  {c(color, fmt_time(remaining))}  remaining")
        print()
        print(f"  {c(color, bar)}  {pct}%")
        print()
        print(c("dim", "  Ctrl+C to stop early"))

        time.sleep(1)

    clear()
    return True

def show_stats():
    sessions = load_sessions()
    if not sessions:
        print(c("dim", "  No sessions recorded yet.\n"))
        return

    print(c("bold", "\n  Session History\n"))
    for day in sorted(sessions.keys(), reverse=True)[:7]:
        entries = sessions[day]
        print(f"  {c('cyan', day)}  —  {len(entries)} pomodoro(s)")
        for e in entries:
            print(f"    {c('dim', e['completed_at'])}  {e['label']}")
    print()

def main():
    pomodoros_done = 0

    clear()
    print()
    print(c("bold", "  🍅 Focus Timer"))
    print(c("dim",  "  Pomodoro-style — 25 min focus / 5 min break\n"))

    show_stats()

    label = input(c("cyan", "  What are you working on? ")).strip() or "Focus session"
    print()

    while True:
        # --- Work session ---
        print(c("bold", f"\n  Starting focus session #{pomodoros_done + 1}…\n"))
        time.sleep(1)
        completed = run_timer(label, WORK_MIN, "red")

        if completed:
            pomodoros_done += 1
            log_completed(label)
            notify("Focus Timer", f"Pomodoro #{pomodoros_done} done! Time for a break.")
            clear()
            print()
            print(c("green", f"  ✓ Pomodoro #{pomodoros_done} complete!"))

        # --- Break ---
        if pomodoros_done % POMODOROS_BEFORE_LONG == 0:
            break_min = LONG_BREAK_MIN
            break_label = "Long break"
        else:
            break_min = SHORT_BREAK_MIN
            break_label = "Short break"

        print(c("dim", f"\n  Up next: {break_label} ({break_min} min)"))
        ans = input(c("cyan", "  Start break? [Y/n] ")).strip().lower()
        if ans == "n":
            print(c("dim", "\n  Skipping break.\n"))
        else:
            run_timer(break_label, break_min, "green")
            notify("Focus Timer", "Break over — back to work!")

        print()
        ans = input(c("cyan", "  Start another focus session? [Y/n] ")).strip().lower()
        if ans == "n":
            clear()
            print(c("bold", "\n  Great work! Here's today's summary:\n"))
            show_stats()
            break

if __name__ == "__main__":
    main()
