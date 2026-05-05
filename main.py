# -*- coding: utf-8 -*-
"""PS-ETW Engine Build-Up Tracker - entry point.

Run from repository root: python main.py  (Python 3 required)
Requires: Python 3.10+, Tkinter (stdlib), openpyxl for Excel exports.
"""
from __future__ import annotations

import sys
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parent / "ps_etw_tracker"
if _APP_ROOT.is_dir():
    sys.path.insert(0, str(_APP_ROOT))


def main():
    from backend.database import init_db
    from ui.app import PSETWApp
    import tkinter as tk

    init_db()

    root = tk.Tk()
    root.title("PS-ETW Engine Build-Up Tracker - Bosch RBIN PS-ETW1")

    try:
        root.iconbitmap(str(Path(__file__).resolve().parent / "ps_etw_tracker" / "assets" / "icon.ico"))
    except Exception:
        pass

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    PSETWApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
