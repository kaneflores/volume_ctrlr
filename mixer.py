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

def run_helper(*args) -> str: #//validated and checked
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

def fetch_sessions() -> list[dict]: #validated and done
    raw =  run_helper("list")
    sessions = []
    for line in raw.splitlines():
        parts = line.strip().split("|")
        if len(parts) != 4:
            continue
        pid, name, vol, muted = parts
        sessions.append({
            "pid": int(pid),
            "name": name,
            "vol": int(vol),
            "muted": muted == "1",
        })
    seen: dict[str, dict] = {}
    for s in sessions:
        key = s["name"].lower()
        if key not in seen or s["vol"] > seen[key]["vol"]:
            seen[key] = s
    return sorted(seen.values(), key=lambda x: x["name"].lower())

def fetch_master() -> int: # validated and done
    try:
        return int(run_helper("masterget"))
    except Exception:
        return 100

class VolumeMixer(tk.Tk):
    def __init__(self): # validated and doen
        super().__init__()
        self.title("Volume Mixer")
        self.resizable(True, False)
        self.configure(bg="#1E1E2E")
        self._widgets: dict = {}
        self._after_id = None
        self._build_ui()
        self.after(100, self._full_refresh)
    
    def _build_ui(self): # note done
        # top bar
        topbar = tk.Frame(self, bg="#1E1E2E", pady = 8, padx =12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="🔊  Volume Mixer", font=("Segoe UI", 14, "bold"), fg="#CDD6F4", bg = "#1E1E2E").pack(side="left")
        tk.Button(topbar, text="⟳  Refresh", command = self._full_refresh,
                    font=("Segoe UI", 10), bg = "#313244", fg="#CDD6F4",
                    activebackground ="#45475A", activeforeground="#CDD6F4",
                    relief="flat", padx =10, pady = 4, cursor="hand2").pack(side="right")
        
        tk.Frame(self, height=1, bg="#313244").pack(fill="x")

        #scrollable channel area
        container = tk.Frame(self, bg="#1E1E2E")
        container.pack(fill="both", expand = True)

        self._canvas = tk.Canvas(container, bg="#1E1E2E", highlightthickness=0, height=320)
        self._canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self._canvas.xview)
        scrollbar.pack(side="bottom", fill="x")
        self._canvas.configure(xscrollcommand=scrollbar.set)

        self._channels_frame = tk.Frame(self._canvas, bg="#1E1E2E")
        self._canvas.create_window((0,0), window=self._channels_frame, anchor="nw")
        self._channels_frame.bind("<Configure>",
                lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))

        tk.Frame(self, height =1, bg="#313244").pack(fill="x")

        # status bar
        self._status_var = tk.StringVar(value="Loading...")
        tk.Label(self, textvariable=self._status_var,
                    font=("Segoe UI",9), fg="#6C7086", bg="#1E1E2E",
                    anchor="w", padx=12, pady=6).pack(fill="x")