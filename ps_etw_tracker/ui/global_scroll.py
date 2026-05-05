"""Bind mouse wheel to scroll the widget under the cursor."""
from __future__ import annotations

import tkinter as tk


def bind_global_mousewheel(root: tk.Tk) -> None:
    def scroll_canvas_y(cv: tk.Canvas, lines: int):
        cv.yview_scroll(lines, "units")

    def scroll_canvas_x(cv: tk.Canvas, lines: int):
        cv.xview_scroll(lines, "units")

    def widget_under_cursor(event):
        try:
            return root.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            return None

    def walk_for_scroll_target(start, want_horizontal: bool):
        w = start
        for _ in range(50):
            if not w:
                break
            cls = w.winfo_class()
            if cls == "Canvas":
                cv = w  # type: ignore
                try:
                    if want_horizontal and str(cv.cget("xscrollcommand")):
                        return cv, "cx"
                    if not want_horizontal and str(cv.cget("yscrollcommand")):
                        return cv, "cy"
                except tk.TclError:
                    pass
            if cls == "Treeview":
                return w, "tv"
            if cls == "Listbox":
                return w, "lb"
            if cls in ("Text", "TText"):
                return w, "txt"
            w = w.master
        return None, None

    def on_wheel(event):
        start = widget_under_cursor(event)
        if not start:
            return
        tgt, kind = walk_for_scroll_target(start, False)
        delta = getattr(event, "delta", 0) or 0
        lines = int(-1 * (delta / 120)) if delta else 0
        if lines == 0:
            return
        try:
            if kind == "cy":
                scroll_canvas_y(tgt, lines)
            elif kind == "tv":
                tgt.yview_scroll(lines, "units")
            elif kind == "lb":
                tgt.yview_scroll(lines, "units")
            elif kind == "txt":
                tgt.yview_scroll(lines, "units")
        except tk.TclError:
            pass

    def on_shift_wheel(event):
        start = widget_under_cursor(event)
        if not start:
            return
        tgt, kind = walk_for_scroll_target(start, True)
        if kind != "cx":
            return
        delta = getattr(event, "delta", 0) or 0
        lines = int(-1 * (delta / 120)) if delta else 0
        if lines == 0:
            return
        try:
            scroll_canvas_x(tgt, lines)
        except tk.TclError:
            pass

    root.bind_all("<MouseWheel>", on_wheel, add="+")
    root.bind_all("<Shift-MouseWheel>", on_shift_wheel, add="+")

    def linux_up(e):
        e.delta = 120
        on_wheel(e)

    def linux_down(e):
        e.delta = -120
        on_wheel(e)

    root.bind_all("<Button-4>", linux_up, add="+")
    root.bind_all("<Button-5>", linux_down, add="+")
