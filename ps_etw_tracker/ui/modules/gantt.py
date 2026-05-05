import tkinter as tk
from tkinter import ttk
from ui.theme import C, F
from backend.scheduler import parse_date, fmt_date
from datetime import date, timedelta


class GanttModule:
    ZOOM_LEVELS = {"Week": 40, "2-Week": 28, "Month": 16, "Quarter": 8}
    STATUS_COLORS = {
        "Complete":    "#2E7D32",
        "In Progress": "#1565C0",
        "Blocked":     "#B71C1C",
        "Delayed":     "#E65100",
        "On Hold":     "#4A148C",
        "Not Started": "#546E7A",
    }
    PLAN_FILL = "#1565C0"
    ACT_FILL = "#43A047"

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.zoom = "Month"
        self.col_w = self.ZOOM_LEVELS["Month"]

    def render(self):
        outer = tk.Frame(self.parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        toolbar = tk.Frame(outer, bg=C["accent_bg"], padx=12, pady=8)
        toolbar.grid(row=0, column=0, sticky="ew")

        tk.Label(toolbar, text="Zoom:", font=F["small"],
                 bg=C["accent_bg"]).pack(side="left")

        zoom_frame = tk.Frame(toolbar, bg=C["border"], padx=1, pady=1)
        zoom_frame.pack(side="left", padx=(4, 16))
        self.zoom_btns = {}
        for level in self.ZOOM_LEVELS:
            btn = tk.Button(
                zoom_frame, text=level,
                font=F["small_b"],
                bg=C["red"] if level == self.zoom else C["card"],
                fg="white" if level == self.zoom else C["text"],
                relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                command=lambda z=level: self._set_zoom(z))
            btn.pack(side="left")
            self.zoom_btns[level] = btn

        ttk.Button(toolbar, text="Refresh Gantt", style="Secondary.TButton",
                   command=self._refresh).pack(side="left")
        ttk.Button(toolbar, text="Export PS", style="Secondary.TButton",
                   command=self._export_png).pack(side="left", padx=(6, 0))

        legend = tk.Frame(toolbar, bg=C["accent_bg"])
        legend.pack(side="right")
        for txt, col in [("Planned", self.PLAN_FILL), ("Actual", self.ACT_FILL)]:
            lf = tk.Frame(legend, bg=C["accent_bg"])
            lf.pack(side="left", padx=(12, 0))
            cv = tk.Canvas(lf, width=14, height=14, bg=C["accent_bg"], highlightthickness=0)
            cv.pack(side="left")
            cv.create_rectangle(2, 4, 12, 10, fill=col, outline="")
            tk.Label(lf, text=txt, font=F["caption"], bg=C["accent_bg"]).pack(side="left", padx=(4, 0))

        gantt_outer = tk.Frame(outer, bg=C["card"])
        gantt_outer.grid(row=1, column=0, sticky="nsew")
        gantt_outer.grid_rowconfigure(0, weight=1)
        gantt_outer.grid_columnconfigure(0, weight=1)

        hscroll = ttk.Scrollbar(gantt_outer, orient="horizontal")
        hscroll.grid(row=1, column=0, sticky="ew")

        vscroll = ttk.Scrollbar(gantt_outer, orient="vertical")
        vscroll.grid(row=0, column=1, sticky="ns")

        self.canvas = tk.Canvas(gantt_outer, bg=C["card"],
                                 xscrollcommand=hscroll.set,
                                 yscrollcommand=vscroll.set,
                                 highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        hscroll.config(command=self.canvas.xview)
        vscroll.config(command=self.canvas.yview)

        self.canvas.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        self.canvas.delete("all")
        acts = self.app.activities
        if not acts:
            self.canvas.create_text(100, 80, text="No activities.",
                                     font=F["h2"], fill=C["muted"], anchor="nw")
            return

        LEFT_W = 320
        ROW_PLAN = 26
        ROW_ACT = 22
        HEADER_H = 46

        dates_sources = []
        for a in acts:
            for key in ("plan_start", "plan_finish", "actual_start", "actual_finish"):
                d = parse_date(a.get(key))
                if d:
                    dates_sources.append(d)

        proj = next((p for p in self.app.projects if p["id"] == self.app.active_project_id), None)
        if proj:
            for key in ("start_date", "target_finish", "forecast_finish"):
                d = parse_date(proj.get(key))
                if d:
                    dates_sources.append(d)

        if not dates_sources:
            self.canvas.create_text(40, 80,
                text="No schedule dates yet.\nUse Edit Project to set Planned Start, then Refresh.",
                font=F["body"], fill=C["muted"], anchor="nw")
            return

        date_start = min(dates_sources) - timedelta(days=3)
        date_end = max(dates_sources) + timedelta(days=14)
        today = date.today()

        all_dates = []
        d = date_start
        while d <= date_end:
            all_dates.append(d)
            d += timedelta(days=1)

        col_w = max(self.col_w, 8)
        total_w = LEFT_W + len(all_dates) * col_w

        segment_month = None
        segment_start_idx = 0
        for i, dd in enumerate(all_dates):
            key = (dd.year, dd.month)
            if segment_month is None:
                segment_month = key
                segment_start_idx = i
            elif key != segment_month:
                x0 = LEFT_W + segment_start_idx * col_w
                x1 = LEFT_W + i * col_w
                ym = date(segment_month[0], segment_month[1], 1)
                self.canvas.create_rectangle(x0, 0, x1, 22, fill=C["steel_light"], outline=C["border"])
                self.canvas.create_text((x0 + x1) / 2, 11, text=ym.strftime("%b %Y"),
                                        font=F["small_b"], fill=C["steel"])
                segment_month = key
                segment_start_idx = i
        if segment_month:
            x0 = LEFT_W + segment_start_idx * col_w
            x1 = LEFT_W + len(all_dates) * col_w
            ym = date(segment_month[0], segment_month[1], 1)
            self.canvas.create_rectangle(x0, 0, x1, 22, fill=C["steel_light"], outline=C["border"])
            self.canvas.create_text((x0 + x1) / 2, 11, text=ym.strftime("%b %Y"),
                                    font=F["small_b"], fill=C["steel"])

        for i, dd in enumerate(all_dates):
            x = LEFT_W + i * col_w
            is_wknd = dd.weekday() >= 5
            is_today = dd == today
            bg = C["red"] if is_today else (C["accent_bg"] if is_wknd else C["card"])
            fg = "white" if is_today else C["muted"]
            self.canvas.create_rectangle(x, 22, x + col_w, HEADER_H, fill=bg, outline=C["border"])
            if col_w >= 12:
                self.canvas.create_text(x + col_w / 2, 34, text=str(dd.day),
                                        font=F["caption"], fill=fg)

        self.canvas.create_rectangle(0, 0, LEFT_W, HEADER_H, fill="#ECEFF1", outline=C["border"])
        self.canvas.create_text(8, 24, text="Activity / Tech / %", anchor="w", font=F["small_b"], fill=C["steel"])

        y = HEADER_H
        cur_major = None
        cur_phase = None

        for a in acts:
            if a["major_phase"] != cur_major:
                cur_major = a["major_phase"]
                cur_phase = None
                self.canvas.create_rectangle(0, y, total_w, y + 22, fill=C["steel"], outline="")
                self.canvas.create_text(10, y + 11, text=f"[ {cur_major} ]",
                                        anchor="w", font=F["small_b"], fill="white")
                y += 22

            if a["phase"] != cur_phase:
                cur_phase = a["phase"]
                self.canvas.create_rectangle(0, y, total_w, y + 18, fill=C["steel_light"], outline=C["border"])
                self.canvas.create_text(14, y + 9, text=f"> {a['phase']}",
                                        anchor="w", font=F["small"], fill="#263238")
                y += 18

            status = a.get("status", "Not Started")
            row_bg = C["red_light"] if status == "Blocked" else (
                     C["amber_row"] if status == "Delayed" else C["card"])
            self.canvas.create_rectangle(0, y, LEFT_W, y + ROW_PLAN, fill=row_bg, outline=C["border"])
            nm = f"#{a['seq_num']} {str(a.get('activity_name',''))[:34]}"
            self.canvas.create_text(8, y + ROW_PLAN // 2, text=nm, anchor="w", font=F["small"], fill="#111")
            self.canvas.create_text(LEFT_W - 8, y + ROW_PLAN // 2,
                                    text=f"{a.get('pct_complete',0)}%",
                                    anchor="e", font=F["caption"], fill=C["text"])

            plan_s = parse_date(a.get("plan_start"))
            plan_f = parse_date(a.get("plan_finish"))
            bar_color = self.STATUS_COLORS.get(status, self.PLAN_FILL)

            if plan_s and plan_f and date_start <= plan_f:
                si = max(0, (plan_s - date_start).days)
                ei = max(si, (plan_f - date_start).days)
                x1 = LEFT_W + si * col_w
                x2 = LEFT_W + (ei + 1) * col_w
                self.canvas.create_rectangle(x1, y + 4, x2, y + ROW_PLAN - 4,
                                             fill=bar_color, outline="")
                if x2 - x1 > 40:
                    self.canvas.create_text(x1 + 4, y + ROW_PLAN // 2, text="PLAN",
                                              anchor="w", font=F["caption"], fill="white")

            act_s = parse_date(a.get("actual_start"))
            act_f = parse_date(a.get("actual_finish"))
            y += ROW_PLAN

            self.canvas.create_rectangle(0, y, LEFT_W, y + ROW_ACT, fill="#FAFAFA", outline=C["border"])
            self.canvas.create_text(22, y + ROW_ACT // 2, text="Actual", anchor="w",
                                    font=F["caption"], fill=C["muted"])

            if act_s:
                end_act = act_f or today
                si = max(0, (act_s - date_start).days)
                ei = max(si, (end_act - date_start).days)
                x1 = LEFT_W + si * col_w
                x2 = LEFT_W + (ei + 1) * col_w
                self.canvas.create_rectangle(x1, y + 3, x2, y + ROW_ACT - 3,
                                             fill=self.ACT_FILL, outline="")
                self.canvas.create_text(x1 + 4, y + ROW_ACT // 2, text="ACT",
                                        anchor="w", font=F["caption"], fill="white")
            else:
                self.canvas.create_text(LEFT_W // 2, y + ROW_ACT // 2,
                                        text="(no actual dates)",
                                        font=F["caption"], fill=C["muted"])

            y += ROW_ACT

        if date_start <= today <= date_end:
            tx = LEFT_W + (today - date_start).days * col_w
            self.canvas.create_line(tx, 0, tx, y, fill=C["red"], width=2)
            self.canvas.create_rectangle(tx - 28, 2, tx + 28, 18, fill=C["red"], outline="")
            self.canvas.create_text(tx, 10, text="TODAY", font=F["caption"], fill="white")

        if proj:
            target = parse_date(proj.get("target_finish"))
            if target and date_start <= target <= date_end:
                tx = LEFT_W + (target - date_start).days * col_w
                self.canvas.create_line(tx, 14, tx, y, fill="#D32F2F", width=2, dash=(5, 4))
                self.canvas.create_text(tx, HEADER_H - 4, text="TARGET", font=F["caption"], fill="#D32F2F")

        self.canvas.configure(scrollregion=(0, 0, total_w, y + 40))

    def _set_zoom(self, level: str):
        self.zoom = level
        self.col_w = self.ZOOM_LEVELS[level]
        for z, btn in self.zoom_btns.items():
            btn.configure(
                bg=C["red"] if z == level else C["card"],
                fg="white" if z == level else C["text"])
        self._draw()

    def _refresh(self):
        from backend.scheduler import run_schedule_and_save
        run_schedule_and_save(self.app.active_project_id)
        self.app.refresh()
        self.app.toast.show("Gantt Refreshed", "Schedule updated", "ok")

    def _export_png(self):
        from tkinter import filedialog
        try:
            fname = filedialog.asksaveasfilename(
                defaultextension=".ps",
                filetypes=[("PostScript", "*.ps"), ("All files", "*.*")],
                title="Export Gantt")
            if fname:
                self.canvas.postscript(file=fname, colormode="color")
                self.app.toast.show("Exported", f"Saved: {fname}", "ok")
        except Exception as e:
            self.app.toast.show("Export Failed", str(e), "err")
