import tkinter as tk
from ui.theme import C, F

NAV_ITEMS = [
    ("dashboard",    "⬛", "Dashboard"),
    ("activities",   "☰",  "Activities"),
    ("gantt",        "▬",  "Gantt"),
    ("calendar",     "📅", "Calendar"),
    ("materials",    "⬡",  "Materials"),
    ("delays",       "⚠",  "Delays & Actions"),
    ("documents",    "📎", "Documents"),
    ("reports",      "⬇",  "Reports"),
]
NAV_ITEMS2 = [
    ("all_projects", "📁", "All Projects"),
    ("settings",     "⚙",  "Settings"),
]


class Sidebar:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=C["steel"], width=220)
        self.frame.pack_propagate(False)
        self._buttons: dict[str, tk.Button] = {}
        self._build()

    def _build(self):
        for tab_id, icon, label in NAV_ITEMS:
            btn = self._make_nav_btn(tab_id, icon, label)
            self._buttons[tab_id] = btn

        tk.Frame(self.frame, bg=C["border"], height=1).pack(
            fill="x", padx=12, pady=4)

        for tab_id, icon, label in NAV_ITEMS2:
            btn = self._make_nav_btn(tab_id, icon, label)
            self._buttons[tab_id] = btn

        tk.Label(self.frame, text="v2.1.0 — Bosch RBIN PS-ETW1",
                 font=F["caption"], bg=C["steel"],
                 fg="#999999").pack(side="bottom", pady=8, padx=14,
                                     anchor="w")

    def _make_nav_btn(self, tab_id: str, icon: str, label: str) -> tk.Button:
        f = tk.Frame(self.frame, bg=C["steel"])
        f.pack(fill="x")

        indicator = tk.Frame(f, width=3, bg=C["steel"])
        indicator.pack(side="left", fill="y")

        btn = tk.Button(
            f,
            text=f"  {icon}   {label}",
            font=F["body"],
            bg=C["steel"], fg=C["steel_light"],
            activebackground="#455A64",
            relief="flat", bd=0,
            anchor="w", padx=10, pady=8,
            cursor="hand2",
            command=lambda t=tab_id: self.app.navigate(t)
        )
        btn.pack(fill="x")
        btn._indicator = indicator
        btn._frame = f
        return btn

    def update(self):
        for tab_id, btn in self._buttons.items():
            if tab_id == self.app.active_tab:
                btn.configure(bg="#2A3840", fg="white", font=F["body_b"])
                btn._indicator.configure(bg=C["red"])
                btn._frame.configure(bg="#2A3840")
            else:
                btn.configure(bg=C["steel"], fg=C["steel_light"], font=F["body"])
                btn._indicator.configure(bg=C["steel"])
                btn._frame.configure(bg=C["steel"])
