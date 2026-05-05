import tkinter as tk
from tkinter import ttk
from ui.theme import C, F
from backend.scheduler import parse_date, fmt_date
from datetime import date, timedelta


class GanttModule:
    ZOOM_LEVELS = {"Week": 40, "2-Week": 28, "Month": 16, "Quarter": 8}
    STATUS_COLORS = {
        "Complete":    "#1B5E20",
        "In Progress": "#1565C0",
        "Blocked":     "#B71C1C",
        "Delayed":     "#E65100",
        "On Hold":     "#4A148C",
        "Not Started": "#757575",
    }

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.zoom = "Month"
        self.col_w = self.ZOOM_LEVELS["Month"]

    def render(self):
        toolbar = tk.Frame(self.parent, bg=C["card"], padx=12, pady=8)
        toolbar.pack(fill="x", pady=(0, 8))

        tk.Label(toolbar, text="Zoom:", font=F["small"],
                 bg=C["card"]).pack(side="left")

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

        ttk.Button(toolbar, text="⟳ Refresh Gantt", style="Secondary.TButton",
                   command=self._refresh).pack(side="left")
        ttk.Button(toolbar, text="⬇ Export PS", style="Secondary.TButton",
                   command=self._export_png).pack(side="left", padx=(6, 0))

        gantt_outer = tk.Frame(self.parent, bg=C["card"])
        gantt_outer.pack(fill="both", expand=True)

        hscroll = ttk.Scrollbar(gantt_outer, orient="horizontal")
        hscroll.pack(side="bottom", fill="x")

        vscroll = ttk.Scrollbar(gantt_outer, orient="vertical")
        vscroll.pack(side="right", fill="y")

        self.canvas = tk.Canvas(gantt_outer, bg=C["card"],
                                 xscrollcommand=hscroll.set,
                                 yscrollcommand=vscroll.set,
                                 highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        hscroll.config(command=self.canvas.xview)
        vscroll.config(command=self.canvas.yview)

        self.canvas.bind("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.bind("<Shift-MouseWheel>",
            lambda e: self.canvas.xview_scroll(-1 * (e.delta // 120), "units"))

        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        acts = self.app.activities
        if not acts:
            self.canvas.create_text(400, 200, text="No activities to display.",
                                     font=F["h2"], fill=C["muted"])
            return

        col_w = self.col_w
        LEFT_W = 300
        ROW_H = 28
        HEADER_H = 44

        all_starts = [parse_date(a["plan_start"]) for a in acts if a.get("plan_start")]
        all_ends = [parse_date(a["plan_finish"]) for a in acts if a.get("plan_finish")]
        if not all_starts:
            self.canvas.create_text(400, 200, text="No planned dates — set project start date.",
                                     font=F["h2"], fill=C["muted"])
            return

        date_start = min(all_starts) - timedelta(days=3)
        date_end = max(all_ends) + timedelta(days=10) if all_ends else date_start + timedelta(days=60)
        today = date.today()

        all_dates = []
        d = date_start
        while d <= date_end:
            all_dates.append(d)
            d += timedelta(days=1)

        total_w = LEFT_W + len(all_dates) * col_w

        segment_start_idx = 0
        segment_month = None
        for i, dd in enumerate(all_dates):
            key = (dd.year, dd.month)
            if segment_month is None:
                segment_month = key
                segment_start_idx = i
            elif key != segment_month:
                x0 = LEFT_W + segment_start_idx * col_w
                x1 = LEFT_W + i * col_w
                ym = date(segment_month[0], segment_month[1], 1)
                self.canvas.create_rectangle(
                    x0, 0, x1, 20,
                    fill=C["steel_light"], outline=C["border"])
                self.canvas.create_text(
                    (x0 + x1) / 2, 10,
                    text=ym.strftime("%b %Y"),
                    font=F["small_b"], fill=C["steel"])
                segment_month = key
                segment_start_idx = i
        if segment_month is not None:
            x0 = LEFT_W + segment_start_idx * col_w
            x1 = LEFT_W + len(all_dates) * col_w
            ym = date(segment_month[0], segment_month[1], 1)
            self.canvas.create_rectangle(
                x0, 0, x1, 20,
                fill=C["steel_light"], outline=C["border"])
            self.canvas.create_text(
                (x0 + x1) / 2, 10,
                text=ym.strftime("%b %Y"),
                font=F["small_b"], fill=C["steel"])

        for i, dd in enumerate(all_dates):
            x = LEFT_W + i * col_w
            is_wknd = dd.weekday() >= 5
            is_today = (dd == today)
            bg = C["red"] if is_today else (C["row_alt"] if is_wknd else C["card"])
            fg = "white" if is_today else (C["muted"])
            self.canvas.create_rectangle(x, 20, x + col_w, HEADER_H,
                                          fill=bg, outline=C["border"])
            if col_w >= 14:
                self.canvas.create_text(x + col_w / 2, 32,
                                         text=str(dd.day), font=F["caption"], fill=fg)

        self.canvas.create_rectangle(0, 0, LEFT_W, HEADER_H,
                                          fill="#FAFAFA", outline=C["border"])
        self.canvas.create_text(10, 22, text="Activity", anchor="w",
                                 font=F["small_b"], fill=C["muted"])
        self.canvas.create_text(220, 22, text="Tech", anchor="w",
                                 font=F["small_b"], fill=C["muted"])
        self.canvas.create_text(265, 22, text="%", anchor="w",
                                 font=F["small_b"], fill=C["muted"])

        y = HEADER_H
        cur_major = None
        cur_phase = None

        for a in acts:
            if a["major_phase"] != cur_major:
                cur_major = a["major_phase"]
                cur_phase = None
                self.canvas.create_rectangle(0, y, total_w, y + 22,
                                              fill=C["steel"], outline="")
                self.canvas.create_text(10, y + 11, text=f"⬛  {cur_major}",
                                         anchor="w", font=F["small_b"],
                                         fill="white")
                y += 22

            if a["phase"] != cur_phase:
                cur_phase = a["phase"]
                self.canvas.create_rectangle(0, y, total_w, y + 20,
                                              fill=C["steel_light"], outline=C["border"])
                self.canvas.create_text(16, y + 10, text=f"▸  {a['phase']}",
                                         anchor="w", font=F["small"],
                                         fill="#111111")
                y += 20

            plan_s = parse_date(a.get("plan_start"))
            plan_f = parse_date(a.get("plan_finish"))
            status = a.get("status", "Not Started")
            bar_color = self.STATUS_COLORS.get(status, C["blue_mid"])

            row_bg = C["red_light"] if status == "Blocked" else (
                     C["amber_row"] if status == "Delayed" else C["card"])
            self.canvas.create_rectangle(0, y, LEFT_W, y + ROW_H,
                                          fill=row_bg, outline=C["border"])
            name_text = f"  #{a['seq_num']}  {a['activity_name'][:35]}"
            self.canvas.create_text(6, y + ROW_H // 2, text=name_text,
                                     anchor="w", font=F["small"], fill="#111111")
            self.canvas.create_text(222, y + ROW_H // 2,
                                     text=(a.get("technician") or "")[:12],
                                     anchor="w", font=F["small"], fill=C["text"])
            self.canvas.create_text(268, y + ROW_H // 2,
                                     text=f"{a['pct_complete']}%",
                                     anchor="w", font=F["small"], fill=C["text"])

            if plan_s and plan_f:
                si = (plan_s - date_start).days
                ei = (plan_f - date_start).days
                x1 = LEFT_W + si * col_w
                x2 = LEFT_W + (ei + 1) * col_w
                self.canvas.create_rectangle(x1, y + 5, x2, y + ROW_H - 5,
                                              fill=bar_color, outline="")
                if (x2 - x1) > 20:
                    self.canvas.create_text(x1 + 4, y + ROW_H // 2,
                                             text=fmt_date(plan_s),
                                             anchor="w", font=F["caption"],
                                             fill="white")
            y += ROW_H

            act_s = parse_date(a.get("actual_start"))
            act_f = parse_date(a.get("actual_finish"))
            if act_s:
                self.canvas.create_rectangle(0, y, LEFT_W, y + 20,
                                              fill="#FCFCFC", outline=C["border"])
                self.canvas.create_text(24, y + 10, text="↳ ACTUAL",
                                         anchor="w", font=F["caption"], fill=C["muted"])
                si = (act_s - date_start).days
                ei = ((act_f or today) - date_start).days
                x1 = LEFT_W + si * col_w
                x2 = LEFT_W + (ei + 1) * col_w
                self.canvas.create_rectangle(x1, y + 4, x2, y + 16,
                                              fill="#2E7D32", outline="")
                y += 20

        if date_start <= today <= date_end:
            tx = LEFT_W + (today - date_start).days * col_w
            self.canvas.create_line(tx, 0, tx, y + 20,
                                     fill=C["red"], width=2)
            self.canvas.create_rectangle(tx - 20, 0, tx + 20, 14,
                                          fill=C["red"], outline="")
            self.canvas.create_text(tx, 7, text="TODAY",
                                     font=F["caption"], fill="white")

        proj = next((p for p in self.app.projects
                     if p["id"] == self.app.active_project_id), None)
        if proj:
            target = parse_date(proj.get("target_finish"))
            if target and date_start <= target <= date_end:
                tx = LEFT_W + (target - date_start).days * col_w
                self.canvas.create_line(tx, 14, tx, y + 20,
                                         fill=C["red"], width=2,
                                         dash=(6, 4))
                self.canvas.create_text(tx, 20, text="TARGET",
                                         font=F["caption"], fill=C["red"])

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
        self.app.toast.show("Gantt Refreshed", "Auto-schedule rerun", "ok")

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
