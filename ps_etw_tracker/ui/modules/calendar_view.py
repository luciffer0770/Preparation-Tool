import tkinter as tk
from tkinter import ttk
from ui.theme import C, F
from backend.scheduler import parse_date, run_schedule_and_save
from datetime import date, timedelta


class CalendarModule:
    STATUS_BG = {
        "Blocked":     C["red_light"],
        "Delayed":     C["amber_row"],
        "In Progress": C["blue_light"],
        "Complete":    C["green_light"],
    }
    STATUS_BORDER = {
        "Blocked":     C["red_dark"],
        "Delayed":     C["amber"],
        "In Progress": C["blue_mid"],
        "Complete":    C["green"],
    }
    MONTHS = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        now = date.today()
        self.year = now.year
        self.month = now.month - 1
        self.selected_day: int | None = None
        self.cycle_index = 0

    def render(self):
        ctrl = tk.Frame(self.parent, bg=C["bg"])
        ctrl.pack(fill="x", pady=(0, 10))

        ttk.Button(ctrl, text="◀ PREV", style="Secondary.TButton",
                   command=self._prev).pack(side="left")
        self.title_lbl = tk.Label(ctrl, text=self._month_title(),
                                   font=F["h2"], bg=C["bg"], fg="#111111")
        self.title_lbl.pack(side="left", padx=16)
        ttk.Button(ctrl, text="NEXT ▶", style="Secondary.TButton",
                   command=self._next).pack(side="left")
        ttk.Button(ctrl, text="Today", style="Ghost.TButton",
                   command=self._go_today).pack(side="left", padx=(12, 0))
        ttk.Button(ctrl, text="⟳ Refresh", style="Ghost.TButton",
                   command=self._refresh).pack(side="left", padx=(8, 0))

        grid_outer = tk.Frame(self.parent, bg=C["bg"])
        grid_outer.pack(fill="both", expand=True)

        self.cal_frame = tk.Frame(grid_outer, bg=C["bg"])
        self.cal_frame.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(grid_outer, bg=C["card"], width=280)
        self.side_frame.pack(side="right", fill="y", padx=(8, 0))
        self.side_frame.pack_propagate(False)

        self._draw_grid()
        self._draw_legend()
        self._draw_sidebar()

    def _draw_grid(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()

        DOW = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        hdr = tk.Frame(self.cal_frame, bg=C["steel"])
        hdr.pack(fill="x")
        for d in DOW:
            tk.Label(hdr, text=d, font=F["small_b"], width=14,
                     bg=C["steel"], fg="white",
                     relief="flat", pady=6).pack(side="left", expand=True)

        year = self.year
        month = self.month + 1
        first_dow = date(year, month, 1).weekday()
        if month == 12:
            days_in_month = (date(year + 1, 1, 1) - timedelta(days=1)).day
        else:
            days_in_month = (date(year, month + 1, 1) - timedelta(days=1)).day

        weeks_frame = tk.Frame(self.cal_frame, bg=C["border"])
        weeks_frame.pack(fill="both", expand=True)

        today = date.today()

        for week in range(6):
            row = tk.Frame(weeks_frame, bg=C["border"])
            row.pack(fill="x", pady=1)
            for dow in range(7):
                cell_num = week * 7 + dow - first_dow + 1
                is_valid = 1 <= cell_num <= days_in_month

                cell_date = date(year, month, cell_num) if is_valid else None

                day_acts = []
                if is_valid and cell_date:
                    day_acts = [
                        a for a in self.app.activities
                        if self._activity_on_date(a, cell_date)
                    ]

                is_today = (cell_date == today) if cell_date else False
                is_wknd = dow >= 5
                dominant = self._dominant_status(day_acts)

                if not is_valid:
                    cell_bg = C["row_alt"]
                elif is_today:
                    cell_bg = C["blue_light"]
                elif day_acts:
                    cell_bg = self.STATUS_BG.get(dominant, C["card"])
                elif is_wknd:
                    cell_bg = C["row_alt"]
                else:
                    cell_bg = C["card"]

                cell = tk.Frame(row, bg=cell_bg, width=120, height=90,
                                 highlightbackground=C["red"] if is_today else C["border"],
                                 highlightthickness=2 if is_today else 1)
                cell.pack(side="left", fill="both", expand=True,
                          padx=1, pady=0)
                cell.pack_propagate(False)

                if is_valid:
                    day_font = (F["body_b"][0], 14, "bold") if is_today else F["body_b"]
                    day_fg = C["red"] if is_today else "#111111"
                    tk.Label(cell, text=str(cell_num), font=day_font,
                             bg=cell_bg, fg=day_fg, anchor="nw").pack(
                        anchor="nw", padx=4, pady=2)

                    for act in day_acts[:2]:
                        border_c = self.STATUS_BORDER.get(act["status"], C["muted"])
                        snippet = tk.Frame(cell, bg=cell_bg,
                                           highlightbackground=border_c,
                                           highlightthickness=0)
                        snippet.pack(fill="x", padx=3, pady=1)
                        tk.Frame(snippet, width=3, bg=border_c).pack(
                            side="left", fill="y")
                        tk.Label(snippet,
                                 text=(act["activity_name"] or "")[:18],
                                 font=F["caption"], bg=cell_bg,
                                 fg=C["text"], anchor="w").pack(
                            side="left", padx=(2, 0), pady=1)

                    if len(day_acts) > 2:
                        tk.Label(cell, text=f"+{len(day_acts)-2} more",
                                 font=F["caption"], bg=cell_bg,
                                 fg=C["muted"]).pack(anchor="w", padx=4)

                    the_day = cell_num
                    cell.bind("<Button-1>",
                              lambda e, d=the_day: self._on_day_click(d))
                    for child in cell.winfo_children():
                        child.bind("<Button-1>",
                                   lambda e, d=the_day: self._on_day_click(d))

    def _draw_sidebar(self):
        for w in self.side_frame.winfo_children():
            w.destroy()

        if not self.selected_day:
            tk.Label(self.side_frame, text="Click a day to see details",
                     font=F["small"], bg=C["card"], fg=C["muted"],
                     wraplength=240).pack(pady=30, padx=16)
            return

        month = self.month + 1
        try:
            cell_date = date(self.year, month, self.selected_day)
        except ValueError:
            return

        day_acts = [a for a in self.app.activities
                    if self._activity_on_date(a, cell_date)]

        header = tk.Frame(self.side_frame, bg=C["card"], padx=14, pady=10)
        header.pack(fill="x")
        tk.Frame(self.side_frame, height=2, bg=C["red"]).pack(fill="x")

        date_str = cell_date.strftime("%A, %d %B %Y")
        tk.Label(header, text=date_str, font=F["h3"],
                 bg=C["card"], fg="#111111", wraplength=240).pack(anchor="w")

        if len(day_acts) > 1:
            tk.Label(header,
                     text=f"{self.cycle_index + 1} of {len(day_acts)} — click again",
                     font=F["caption"], bg=C["card"], fg=C["muted"]).pack(anchor="w")

        ttk.Button(header, text="✕", style="Ghost.TButton",
                   command=self._close_sidebar).pack(anchor="e")

        if not day_acts:
            tk.Label(self.side_frame, text="No activities this day.",
                     font=F["small"], bg=C["card"], fg=C["muted"]).pack(pady=20)
            return

        act = day_acts[self.cycle_index % len(day_acts)]

        body = tk.Frame(self.side_frame, bg=C["card"], padx=14, pady=12)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=act["activity_name"], font=F["h3"],
                 bg=C["card"], fg="#111111", wraplength=240,
                 justify="left").pack(anchor="w", pady=(0, 10))

        fields = [
            ("Phase",       act.get("phase", "—")),
            ("Owner",       act.get("technician", "—")),
            ("Status",      act.get("status", "—")),
            ("% Done",      f"{act.get('pct_complete', 0)}%"),
            ("Plan Start",  act.get("plan_start", "—")),
            ("Plan Finish", act.get("plan_finish", "—")),
            ("Act. Start",  act.get("actual_start", "—") or "—"),
            ("Act. Finish", act.get("actual_finish", "—") or "—"),
            ("Est. Hours",  f"{act.get('est_hours', 0)}h"),
        ]
        for label, value in fields:
            row = tk.Frame(body, bg=C["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label + ":", font=F["small"],
                     bg=C["card"], fg=C["muted"], width=10,
                     anchor="w").pack(side="left")
            tk.Label(row, text=value, font=F["small"],
                     bg=C["card"], fg="#111111",
                     anchor="w").pack(side="left")

        ttk.Button(body, text="View in Activities", style="Secondary.TButton",
                   command=lambda: self.app.navigate("activities")).pack(
            pady=(12, 0), anchor="w")

    def _draw_legend(self):
        leg = tk.Frame(self.parent, bg=C["card"], padx=12, pady=8)
        leg.pack(fill="x", pady=(8, 0))
        leg.configure(highlightbackground=C["border"], highlightthickness=1)

        items = [
            (C["green_light"],  C["green"],    "Complete"),
            (C["blue_light"],   C["blue_mid"], "In Progress"),
            (C["amber_row"],    C["amber"],    "Delayed"),
            (C["red_light"],    C["red_dark"], "Blocked"),
            (C["card"],         C["muted"],    "Not Started"),
            (C["row_alt"],      C["muted"],    "Weekend"),
        ]
        for bg, fg, label in items:
            li = tk.Frame(leg, bg=C["card"])
            li.pack(side="left", padx=(0, 16))
            swatch = tk.Canvas(li, width=14, height=14, bg=C["card"],
                                highlightthickness=0)
            swatch.create_rectangle(0, 0, 14, 14, fill=bg,
                                     outline=fg)
            swatch.pack(side="left", padx=(0, 4))
            tk.Label(li, text=label, font=F["small"],
                     bg=C["card"], fg=C["text"]).pack(side="left")

    def _on_day_click(self, day: int):
        month = self.month + 1
        try:
            cell_date = date(self.year, month, day)
        except ValueError:
            return
        day_acts = [a for a in self.app.activities
                    if self._activity_on_date(a, cell_date)]
        if not day_acts:
            self.selected_day = None
            self._draw_sidebar()
            return
        if self.selected_day == day:
            self.cycle_index += 1
            if self.cycle_index >= len(day_acts):
                self.selected_day = None
                self.cycle_index = 0
                self._draw_sidebar()
                return
        else:
            self.selected_day = day
            self.cycle_index = 0
        self._draw_sidebar()

    def _close_sidebar(self):
        self.selected_day = None
        self.cycle_index = 0
        self._draw_sidebar()

    def _activity_on_date(self, act: dict, d: date) -> bool:
        ps = parse_date(act.get("plan_start"))
        pf = parse_date(act.get("plan_finish"))
        return bool(ps and pf and ps <= d <= pf)

    def _dominant_status(self, acts: list) -> str:
        if not acts:
            return "Not Started"
        for s in ("Blocked", "Delayed", "In Progress"):
            if any(a["status"] == s for a in acts):
                return s
        if all(a["status"] == "Complete" for a in acts):
            return "Complete"
        return "Not Started"

    def _prev(self):
        self.month -= 1
        if self.month < 0:
            self.month = 11
            self.year -= 1
        self.selected_day = None
        self.title_lbl.configure(text=self._month_title())
        self._draw_grid()
        self._draw_sidebar()

    def _next(self):
        self.month += 1
        if self.month > 11:
            self.month = 0
            self.year += 1
        self.selected_day = None
        self.title_lbl.configure(text=self._month_title())
        self._draw_grid()
        self._draw_sidebar()

    def _go_today(self):
        now = date.today()
        self.year = now.year
        self.month = now.month - 1
        self.selected_day = None
        self.title_lbl.configure(text=self._month_title())
        self._draw_grid()
        self._draw_sidebar()

    def _refresh(self):
        run_schedule_and_save(self.app.active_project_id)
        self.app.refresh()
        self.app.toast.show("Refreshed", "Calendar updated", "ok")

    def _month_title(self) -> str:
        return f"{self.MONTHS[self.month]}  {self.year}"
