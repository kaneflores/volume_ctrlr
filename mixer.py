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