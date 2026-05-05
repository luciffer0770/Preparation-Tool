import tkinter as tk
from tkinter import ttk
from ui.theme import C, F


class TopBar:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=C["card"], height=48)
        self.frame.pack_propagate(False)

        red_border = tk.Frame(parent, bg=C["red"], height=2)
        red_border.pack(side="top", fill="x")

        self._build()

    def _build(self):
        left = tk.Frame(self.frame, bg=C["card"])
        left.pack(side="left", fill="y", padx=12)

        brand_canvas = tk.Canvas(left, width=28, height=28, bg=C["card"],
                                  highlightthickness=0)
        brand_canvas.create_oval(1, 1, 27, 27, fill=C["black"], outline="")
        brand_canvas.create_text(14, 14, text="B", fill="white",
                                  font=(F["h2"][0], 11, "bold"))
        brand_canvas.pack(side="left", padx=(0, 6), pady=10)

        tk.Label(left, text="BOSCH", font=F["h2"], bg=C["card"],
                 fg=C["black"]).pack(side="left")

        tk.Frame(left, width=1, bg=C["border"]).pack(side="left", fill="y",
                                                       padx=10, pady=8)
        tk.Label(left, text="PS-ETW Engine Build-Up Tracker",
                 font=F["body_b"], bg=C["card"],
                 fg="#111111").pack(side="left")

        tk.Frame(left, width=1, bg=C["border"]).pack(side="left", fill="y",
                                                       padx=10, pady=8)

        pill_frame = tk.Frame(left, bg=C["border"], padx=1, pady=1)
        self.pill_btn = tk.Button(
            pill_frame, text="Loading...", font=F["small_b"],
            bg=C["card"], fg="#111111", relief="flat", bd=0,
            padx=10, pady=4, cursor="hand2",
            command=self._open_switcher)
        self.pill_btn.pack()
        pill_frame.pack(side="left")

        right = tk.Frame(self.frame, bg=C["card"])
        right.pack(side="right", fill="y", padx=12)

        av = tk.Canvas(right, width=26, height=26, bg=C["card"],
                       highlightthickness=0)
        av.create_oval(0, 0, 26, 26, fill=C["steel"], outline="")
        av.create_text(13, 13, text="RS", fill="white", font=F["caption"])
        av.pack(side="left", padx=(0, 6), pady=11)

        tk.Label(right, text="Ravi Sharma", font=F["small"],
                 bg=C["card"], fg=C["text"]).pack(side="left", padx=(0, 12))

        tk.Button(right, text="⚙", font=(F["body"][0], 14),
                  bg=C["card"], fg=C["text"], relief="flat", bd=0,
                  cursor="hand2",
                  command=lambda: self.app.navigate("settings")).pack(side="left")

    def update(self):
        proj_id = self.app.active_project_id
        if proj_id:
            proj = next((p for p in self.app.projects if p["id"] == proj_id), None)
            if proj:
                text = f"{proj['code']}  |  {proj['name']}  ▾"
                self.pill_btn.configure(text=text)
            else:
                self.pill_btn.configure(text="No project selected  ▾")
        else:
            self.pill_btn.configure(text="Select project  ▾")

    def _open_switcher(self):
        from ui.modules.project_switcher import ProjectSwitcherDrawer
        ProjectSwitcherDrawer(self.app)
