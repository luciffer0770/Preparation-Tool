import tkinter as tk
from ui.theme import C, F


class ToastManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._active: list[tk.Toplevel] = []

    def show(self, title: str, message: str, kind: str = "ok", duration_ms: int = 3500):
        colors = {
            "ok":   (C["green"],    C["green_light"]),
            "warn": (C["amber"],    C["amber_light"]),
            "err":  (C["red_dark"], C["red_light"]),
        }
        border_col, bg_col = colors.get(kind, colors["ok"])

        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg=bg_col)

        self.root.update_idletasks()
        rw = self.root.winfo_x() + self.root.winfo_width()
        rh = self.root.winfo_y() + self.root.winfo_height()
        offset = 20 + len(self._active) * 80
        toast.geometry(f"300x68+{rw - 320}+{rh - offset - 80}")

        outer = tk.Frame(toast, bg=border_col, padx=3)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=bg_col, padx=12, pady=10)
        inner.pack(fill="both", expand=True)

        icons = {"ok": "✓", "warn": "⚠", "err": "✕"}
        tk.Label(inner, text=icons.get(kind, "✓"),
                 font=(F["h2"][0], 14, "bold"),
                 bg=bg_col, fg=border_col).pack(side="left", padx=(0, 10))

        text_frame = tk.Frame(inner, bg=bg_col)
        text_frame.pack(side="left")
        tk.Label(text_frame, text=title, font=F["body_b"],
                 bg=bg_col, fg="#111111").pack(anchor="w")
        tk.Label(text_frame, text=message, font=F["small"],
                 bg=bg_col, fg=C["text"]).pack(anchor="w")

        self._active.append(toast)

        def dismiss():
            toast.destroy()
            if toast in self._active:
                self._active.remove(toast)

        self.root.after(duration_ms, dismiss)
