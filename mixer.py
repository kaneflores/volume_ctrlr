"""
mixer.py - Per-application volume mixer for Windows
Requires: Python 3.8+, tkinter (bundled with python)
The compiled volume_helper.exe must sit in the same folder as the script.

Run: python mixer.py
"""

import subprocess
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(SCRIPT_DIR, "volume_helper.exe")

REFRESH_INTERVAL_MS = 3000
SLIDER_WIDTH = 22
CHANNEL_WIDTH = 110

ICONS = {
    "chrome.exe":   "🌐",
    "firefox.exe":  "🦊",
    "msedge.exe":   "🔷",
    "discord.exe":  "💬",
    "spotify.exe":  "🎵",
    "teams.exe":    "👥",
    "slack.exe":    "💼",
    "obs64.exe":    "📹",
    "obs32.exe":    "📹",
    "vlc.exe":      "🎬",
    "zoom.exe":     "📞",
}

def run_helper(*args) -> str:
    if not os.path.isfile(HELPER):
        raise FileNotFoundError(
            f"volume_helper.exe not found at:\n{HELPER}\n\n"
            "Please compile it first with:\n"
            "gcc volume_helper.c -o volume_helper.exe -lole32 -loleaut32 -luuid -lpsapi"
        )
    result = subprocess.run(
        [HELPER, *[str(a) for a in args]],
        capture_output = True, text = True, timeout = 5
    )
    return result.stdout.strip()
