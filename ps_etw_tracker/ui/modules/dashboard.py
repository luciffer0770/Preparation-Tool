import tkinter as tk
from tkinter import ttk
from ui.theme import C, F
from datetime import date


class DashboardModule:
    def __init__(self, parent: tk.Frame, app):
        self.parent = parent
        self.app = app

    def render(self):
        proj_id = self.app.active_project_id
        if not proj_id:
            tk.Label(self.parent, text="No project selected.",
                     font=F["h2"], bg=C["bg"]).pack(pady=40)
            return

        proj = next((p for p in self.app.projects if p["id"] == proj_id), {})
        acts = self.app.activities
        mats = self.app.materials
        delays = self.app.delays

        self._project_header(proj)

        self._kpi_strip(acts, mats, delays)

        self._health_band(proj)

        cols = tk.Frame(self.parent, bg=C["bg"])
        cols.pack(fill="both", expand=True, pady=(12, 0))

        left_col = tk.Frame(cols, bg=C["bg"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right_col = tk.Frame(cols, bg=C["bg"])
        right_col.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self._status_breakdown(left_col, acts)
        self._phase_completion(left_col, acts)
        self._alerts_panel(right_col, acts, mats)

    def _project_header(self, proj: dict):
        card = tk.Frame(self.parent, bg=C["card"], padx=16, pady=12,
                        relief="flat", bd=0)
        card.pack(fill="x", pady=(0, 12))
        self._card_border(card)

        top_row = tk.Frame(card, bg=C["card"])
        top_row.pack(fill="x")

        tk.Label(top_row, text=proj.get("code", ""),
                 font=(F["mono"][0], 13, "bold"),
                 bg=C["card"], fg=C["red"]).pack(side="left")
        tk.Label(top_row, text=f"  {proj.get('name','')}",
                 font=F["h1"], bg=C["card"], fg="#111111").pack(side="left")

        btn_frame = tk.Frame(card, bg=C["card"])
        btn_frame.pack(side="right", anchor="n")
        ttk.Button(btn_frame, text="Edit Project", style="Secondary.TButton",
                   command=lambda: self._edit_project_dialog(proj)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="⬇ Export Report", style="Primary.TButton",
                   command=lambda: self._export_summary()).pack(side="left")

        meta = tk.Frame(card, bg=C["card"])
        meta.pack(fill="x", pady=(4, 0))
        meta_text = (f"Engine: {proj.get('engine_type','—')}   |   "
                     f"Serial: {proj.get('serial','—')}   |   "
                     f"Trolley: {proj.get('trolley_code','—')} {proj.get('trolley_location','')}   |   "
                     f"PM: {proj.get('pm_name','—')}   |   "
                     f"As of {date.today().strftime('%d %b %Y')}")
        tk.Label(meta, text=meta_text, font=F["small"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w")

    def _kpi_strip(self, acts, mats, delays):
        total = len(acts)
        done = sum(1 for a in acts if a["status"] == "Complete")
        delayed = sum(1 for a in acts if a["status"] == "Delayed")
        blocked = sum(1 for a in acts if a["status"] == "Blocked")
        mat_risk = sum(1 for m in mats if m.get("risk_flag") == "AT RISK")
        open_actions = sum(1 for d in delays if d.get("delay_status") != "Closed")
        pct = round(done / total * 100) if total > 0 else 0

        strip = tk.Frame(self.parent, bg=C["bg"])
        strip.pack(fill="x", pady=(0, 12))

        kpi_data = [
            ("% COMPLETE",     f"{pct}%",   f"of {total} activities", C["red"]),
            ("ACTIVITIES DONE", str(done),   "activities",             C["green"]),
            ("DELAYED",         str(delayed),"activities",             C["amber"]),
            ("BLOCKED",         str(blocked),"activities",             C["red_dark"]),
            ("MATERIAL RISKS",  str(mat_risk),"items at risk",         C["red"]),
            ("OPEN ACTIONS",   str(open_actions),"items",              C["amber"]),
        ]
        for i, (label, value, sub, border_col) in enumerate(kpi_data):
            self._kpi_card_grid(strip, label, value, sub, border_col, i)

    def _kpi_card_grid(self, parent, label, value, sub, border_col, col):
        card = tk.Frame(parent, bg=C["card"], padx=14, pady=14)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))
        parent.grid_columnconfigure(col, weight=1)

        accent = tk.Frame(card, width=4, bg=border_col)
        accent.pack(side="left", fill="y", padx=(0, 10))

        content = tk.Frame(card, bg=C["card"])
        content.pack(side="left", fill="both", expand=True)

        tk.Label(content, text=label, font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w")
        tk.Label(content, text=value, font=F["kpi_sm"],
                 bg=C["card"], fg="#000000").pack(anchor="w")
        tk.Label(content, text=sub, font=F["small"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w")
        self._card_border(card)

    def _health_band(self, proj):
        band = tk.Frame(self.parent, bg=C["row_alt"], padx=16, pady=10)
        band.pack(fill="x", pady=(0, 12))
        self._card_border(band)

        items = [
            ("PLAN START",       proj.get("start_date", "—")),
            ("TARGET FINISH",    proj.get("target_finish", "—")),
            ("FORECAST FINISH",  proj.get("forecast_finish") or proj.get("target_finish", "—")),
            ("DAYS REMAINING",   "—"),
            ("SLIPPAGE",         "—"),
        ]
        for label, value in items:
            f = tk.Frame(band, bg=C["row_alt"])
            f.pack(side="left", padx=(0, 28))
            tk.Label(f, text=label, font=F["caption"],
                     bg=C["row_alt"], fg=C["muted"]).pack(anchor="w")
            tk.Label(f, text=value, font=F["body_b"],
                     bg=C["row_alt"], fg="#000000").pack(anchor="w")

        hf = tk.Frame(band, bg=C["row_alt"])
        hf.pack(side="left")
        tk.Label(hf, text="HEALTH SCORE", font=F["caption"],
                 bg=C["row_alt"], fg=C["muted"]).pack(anchor="w")
        chip_bg = C["amber_light"]
        chip_fg = C["amber"]
        chip_text = "⚠ Minor Delay"
        tk.Label(hf, text=chip_text, font=F["small_b"],
                 bg=chip_bg, fg=chip_fg, padx=8, pady=3).pack(anchor="w")

    def _status_breakdown(self, parent, acts):
        card = tk.Frame(parent, bg=C["card"])
        card.pack(fill="x", pady=(0, 12))
        self._card_border(card)

        header = tk.Frame(card, bg=C["card"], padx=14, pady=10)
        header.pack(fill="x", side="top")
        tk.Label(header, text="Activity Status Breakdown",
                 font=F["h3"], bg=C["card"], fg="#111111").pack(side="left")
        tk.Label(header, text=f"{len(acts)} activities",
                 font=F["caption"], bg=C["card"], fg=C["muted"]).pack(side="right")

        body = tk.Frame(card, bg=C["card"], padx=14, pady=(0, 14))
        body.pack(fill="x")

        total = len(acts)
        if total == 0:
            return
        status_counts = {}
        for a in acts:
            status_counts[a["status"]] = status_counts.get(a["status"], 0) + 1

        bar_data = [
            ("Complete",    C["green"],    status_counts.get("Complete", 0)),
            ("In Progress", C["blue_mid"], status_counts.get("In Progress", 0)),
            ("Not Started", C["muted"],    status_counts.get("Not Started", 0)),
            ("Blocked",     C["red_dark"], status_counts.get("Blocked", 0)),
            ("Delayed",     C["amber"],    status_counts.get("Delayed", 0)),
            ("On Hold",     C["purple"],   status_counts.get("On Hold", 0)),
        ]

        bar_canvas = tk.Canvas(body, height=24, bg=C["card"],
                                highlightthickness=0)
        bar_canvas.pack(fill="x", pady=(0, 8))

        def draw_bar(event=None):
            bar_canvas.delete("all")
            w = bar_canvas.winfo_width()
            if w < 10:
                return
            x = 0
            for (_label, color, count) in bar_data:
                if count == 0:
                    continue
                bw = int((count / total) * w)
                bar_canvas.create_rectangle(x, 2, x + bw - 1, 22,
                                             fill=color, outline="")
                if bw > 20:
                    bar_canvas.create_text(x + bw // 2, 12, text=str(count),
                                           fill="white",
                                           font=F["small_b"])
                x += bw

        bar_canvas.bind("<Configure>", draw_bar)
        bar_canvas.after(50, draw_bar)

        legend = tk.Frame(body, bg=C["card"])
        legend.pack(fill="x")
        for (label, color, count) in bar_data:
            li = tk.Frame(legend, bg=C["card"])
            li.pack(side="left", padx=(0, 14))
            swatch = tk.Canvas(li, width=12, height=12, bg=C["card"],
                                highlightthickness=0)
            swatch.create_rectangle(0, 0, 12, 12, fill=color, outline="")
            swatch.pack(side="left", padx=(0, 4))
            tk.Label(li, text=f"{label} ({count})", font=F["small"],
                     bg=C["card"], fg=C["text"]).pack(side="left")

    def _phase_completion(self, parent, acts):
        card = tk.Frame(parent, bg=C["card"])
        card.pack(fill="x")
        self._card_border(card)

        header = tk.Frame(card, bg=C["card"], padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Phase Completion",
                 font=F["h3"], bg=C["card"], fg="#111111").pack(side="left")

        body = tk.Frame(card, bg=C["card"], padx=14, pady=(0, 14))
        body.pack(fill="x")

        phase_map: dict[str, dict] = {}
        for a in acts:
            ph = a["phase"]
            if ph not in phase_map:
                phase_map[ph] = {"total": 0, "done": 0}
            phase_map[ph]["total"] += 1
            if a["status"] == "Complete":
                phase_map[ph]["done"] += 1

        for ph, stats in phase_map.items():
            row = tk.Frame(body, bg=C["card"])
            row.pack(fill="x", pady=2)

            tk.Label(row, text=ph, font=F["small"], width=22,
                     bg=C["card"], fg="#111111", anchor="w").pack(side="left")
            tk.Label(row, text=f"{stats['done']}/{stats['total']}",
                     font=F["small"], width=8,
                     bg=C["card"], fg=C["muted"], anchor="e").pack(side="left")

            bar_f = tk.Frame(row, bg=C["row_alt"],
                              height=8)
            bar_f.pack(side="left", fill="x", expand=True, padx=6)

            pct = int((stats["done"] / stats["total"]) * 100) if stats["total"] else 0
            fill = tk.Frame(bar_f, bg=C["red"], height=8)
            fill.place(relwidth=pct / 100, relheight=1)

            tk.Label(row, text=f"{pct}%", font=F["small"], width=5,
                     bg=C["card"], fg=C["text"], anchor="e").pack(side="left")

    def _alerts_panel(self, parent, acts, mats):
        card = tk.Frame(parent, bg=C["card"])
        card.pack(fill="both", expand=True)
        self._card_border(card)

        header = tk.Frame(card, bg=C["card"], padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🚨 Live Alerts",
                 font=F["h3"], bg=C["card"], fg="#111111").pack(side="left")
        ttk.Button(header, text="⟳ Refresh", style="Secondary.TButton",
                   command=lambda: [self.app.refresh(),
                                    self.app.toast.show("Refreshed", "Alerts updated", "ok")]
                   ).pack(side="right")

        body = tk.Frame(card, bg=C["card"], padx=14, pady=(0, 14))
        body.pack(fill="both", expand=True)

        alerts = []
        for a in acts:
            if a["status"] == "Blocked":
                alerts.append(("CRIT", a["activity_name"],
                                f"Blocked. Phase: {a['phase']}. Action required."))
            elif a["status"] == "Delayed":
                d = a.get("delay_d") or 1
                alerts.append(("CRIT", a["activity_name"],
                                f"Delayed by {d} day(s). Float: {a.get('float_d',0)}d"))
            elif a["status"] not in ("Complete",) and (a.get("float_d") or 0) <= 2:
                alerts.append(("WARN", a["activity_name"],
                                f"Only {a.get('float_d',0)} day(s) of float remaining."))
        for m in mats:
            oa = str(m.get("order_alert", "") or "")
            if oa.startswith("ORDER NOW"):
                alerts.append(("CRIT", m["description"],
                                f"Not ordered. {m['part_number']} — order date passed."))
        for a in acts:
            if a["status"] == "Complete" and a.get("actual_finish"):
                alerts.append(("INFO", a["activity_name"],
                                f"Completed {a['actual_finish']}."))

        if not alerts:
            tk.Label(body, text="✓  ALL CLEAR — No active issues",
                     font=F["body_b"], bg=C["card"], fg=C["green"]).pack(pady=20)
            return

        for kind, title, desc in alerts[:10]:
            self._alert_row(body, kind, title, desc)

    def _alert_row(self, parent, kind, title, desc):
        colors = {
            "CRIT": (C["red_dark"],   C["red_light"],   "CRITICAL"),
            "WARN": (C["amber"],      C["amber_light"], "WARNING"),
            "INFO": (C["green"],      C["green_light"], "INFO"),
        }
        border_c, bg_c, tag = colors.get(kind, colors["INFO"])

        outer = tk.Frame(parent, bg=border_c, padx=3, pady=0)
        outer.pack(fill="x", pady=(0, 6))
        inner = tk.Frame(outer, bg=bg_c, padx=10, pady=7, cursor="hand2")
        inner.pack(fill="x")

        head = tk.Frame(inner, bg=bg_c)
        head.pack(fill="x")
        tk.Label(head, text=tag, font=F["small_b"],
                 bg=border_c, fg="white",
                 padx=5, pady=1).pack(side="left", padx=(0, 8))
        tk.Label(head, text=title, font=F["small_b"],
                 bg=bg_c, fg="#111111").pack(side="left")

        tk.Label(inner, text=desc, font=F["small"],
                 bg=bg_c, fg=C["text"], anchor="w").pack(fill="x", pady=(2, 0))

        inner.bind("<Button-1>",
                   lambda e: self.app.navigate("activities"))

    def _card_border(self, frame):
        frame.configure(highlightbackground=C["border"],
                        highlightthickness=1)

    def _edit_project_dialog(self, proj):
        from ui.modules.project_switcher import ProjectEditDialog
        ProjectEditDialog(self.app, proj)

    def _export_summary(self):
        from ui.modules.reports import export_summary
        export_summary(self.app)
