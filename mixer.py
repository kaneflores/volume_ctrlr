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
    
    def _build_ui(self): # revalidated
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
    
    def _make_channel(self, parent, key, label, icon, vol, muted, on_vol, on_mute):
        col = len(self._widgets)
        frame = tk.Frame(parent, bg="#181825", bd=0,
                        highlightbackground="#313244", highlightthickness=1,
                        padx=8, pady=10, width=CHANNEL_WIDTH)
        frame.grid(row=0, column=col, sticky="ns", padx=4, pady=8)
        frame.grid_propagate(False)

        tk.Label(frame, text=icon, font=("Segoe UI", 22),
                bg="#181825", fg="#CDD6F4").pack()
        tk.Label(frame, text=label, font=("Segoe UI", 9),
                fg="#BAC2DE", bg="#181825",
                wraplength=CHANNEL_WIDTH - 16, justify = "center").pack(pady=(2,6))
        
        vol_var = tk.IntVar(value=vol)
        pct_lbl = tk.Label(frame, text=f"{vol}%", font=("Segoe UI", 11, "bold"),
                            fg = "#CDD6F4", bg="#181825")
        pct_lbl.pack()

        slider = tk.Scale(frame, from_=100, to=0, orient="vertical",
                            variable= vol_var, length=120, width=SLIDER_WIDTH,
                            showvalue=False, sliderlength=16,
                            bg="#181825", fg = "#CDD6F4", troughcolor="#313244",
                            activebackground="#89B4FA", highlightthickness=0,
                            command=lambda v, k=key, lbl=pct_lbl, cb=on_vol:
                                self._slider_moved(v, k, lbl, cb))
        slider.pack(pady=6)

        mute_btn = tk.Button(frame,
                            text="🔇 Muted" if muted else "🔊  Live",
                            font=("Segoe UI", 8),
                            bg= "#45475A" if muted else "#313244",
                            fg="#CDD6F4", activebackground="#585B70",
                            activeforeground="#CDD6F4", relief="flat",
                            padx = 6, pady=3, cursor="hand2",
                            command=lambda k=key, cb=on_mute: cb(k))
        mute_btn.pack(pady=(2,0))

        return {"frame": frame, "slider": slider, "vol_var": vol_var,
                "pct_lbl": pct_lbl, "mute_btn": mute_btn}
    
    def _slider_moved(self, value, key, lbl, callback): # done updated python and added type settiings
        v = int(float(value))#checkpont
        lbl.config(text=f"{v}%")
        callback(key, v)
    
    def _full_refresh(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._status_var.set("Refreshing...")
        #
        threading.Thread(target=self._refresh_worker, daemon=True).start()
    
    def _refresh_worker(self):
        try:
            sessions = fetch_sessions()
            master = fetch_master()
            self.after(0, lambda: self._apply_refresh(sessions, master))
        except FileNotFoundError as e:
            self.after(0, lambda: messagebox.showerror("Helper not found", str(e)))
        except Exception as e:
            self.after(0, lambda: self._status_var.set(f"Error: {e}"))
        #done and validated

    def _apply_refresh(self, sessions, master):
        for w in self._widgets.values():
            w["frame"].destroy()
        self._widgets.clear()

        #master channel done
        def set_master(key,vol):
            # validated andone
            threading.Thread(target=lambda: run_helper("master", vol), daemon=True).start()

        def mute_master(key): #done 
            cur = self._widgets["__master__"]["vol_var"].get()
            new_vol = 0 if cur > 0 else 50
            self._widgets["__master__"]["slider"].set(new_vol)
            set_master(key, new_vol)
        
        w = self._make_channel(self._channels_frame, "__master__", "Master", "🔊",
                               master, False, on_vol=set_master, on_mute=mute_master)
        w["frame"].config(highlightbackground="#89B4FA", highlightthickness =1)
        self._widgets["__master__"]= w

        #app channels
        for s in sessions:
            pid, name, vol, muted = s["pid"], s["name"], s["vol"], s["muted"]
            icon = get_icon(name)
            display = name[:-4] if name.lower().endswith(".exe") else name
            