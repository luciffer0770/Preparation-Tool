import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import C, F
from backend.database import db_execute, db_fetchone, get_activities, sync_delays
from backend.scheduler import run_schedule_and_save, compute_derived


class ActivitiesModule:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.filter_phase = "All"
        self.filter_status = "All"
        self.filter_dept = "All"
        self.search_var = tk.StringVar()
        self.sort_col = "#"
        self.sort_reverse = False

    def render(self):
        toolbar = tk.Frame(self.parent, bg=C["card"], padx=12, pady=8)
        toolbar.pack(fill="x", pady=(0, 8))
        self._card_border(toolbar)

        config = self.app.config
        phases = ["All"] + config.get("phases_mech", []) + config.get("phases_elec", [])
        statuses = ["All"] + config.get("status", [])
        depts = ["All"] + config.get("department", [])

        tk.Label(toolbar, text="Phase:", font=F["small"],
                 bg=C["card"]).pack(side="left")
        phase_cb = ttk.Combobox(toolbar, values=phases, width=18,
                                 state="readonly", font=F["small"])
        phase_cb.set(self.filter_phase)
        phase_cb.pack(side="left", padx=(4, 10))
        phase_cb.bind("<<ComboboxSelected>>",
                      lambda e: self._filter_change("phase", phase_cb.get()))

        tk.Label(toolbar, text="Status:", font=F["small"],
                 bg=C["card"]).pack(side="left")
        status_cb = ttk.Combobox(toolbar, values=statuses, width=14,
                                  state="readonly", font=F["small"])
        status_cb.set(self.filter_status)
        status_cb.pack(side="left", padx=(4, 10))
        status_cb.bind("<<ComboboxSelected>>",
                       lambda e: self._filter_change("status", status_cb.get()))

        tk.Label(toolbar, text="Dept:", font=F["small"],
                 bg=C["card"]).pack(side="left")
        dept_cb = ttk.Combobox(toolbar, values=depts, width=10,
                                state="readonly", font=F["small"])
        dept_cb.set(self.filter_dept)
        dept_cb.pack(side="left", padx=(4, 16))
        dept_cb.bind("<<ComboboxSelected>>",
                     lambda e: self._filter_change("dept", dept_cb.get()))

        tk.Label(toolbar, text="🔍", font=F["body"],
                 bg=C["card"]).pack(side="left")
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var,
                                  width=24, font=F["small"])
        search_entry.pack(side="left", padx=(4, 0))
        self._trace_search()

        ttk.Button(toolbar, text="+ Add Activity", style="Primary.TButton",
                   command=self._add_activity_dialog).pack(side="right", padx=(6, 0))
        ttk.Button(toolbar, text="⬇ Export Excel", style="Secondary.TButton",
                   command=self._export_excel).pack(side="right", padx=(6, 0))
        ttk.Button(toolbar, text="⟳ Auto-Schedule", style="Secondary.TButton",
                   command=self._run_auto_schedule).pack(side="right", padx=(6, 0))

        self.count_var = tk.StringVar(value="")
        tk.Label(self.parent, textvariable=self.count_var,
                 font=F["small"], bg=C["bg"], fg=C["muted"]).pack(
            anchor="w", pady=(0, 4))

        tbl_frame = tk.Frame(self.parent, bg=C["card"])
        tbl_frame.pack(fill="both", expand=True)
        self._card_border(tbl_frame)

        cols = (
            "#", "Phase", "Activity", "Tech", "Dept",
            "Priority", "Plan Start", "Plan Finish", "Dur", "Float",
            "% Done", "Status", "Est h", "Act h",
            "Act Start", "Act Finish", "Delay", "Alert",
        )
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                  selectmode="browse")

        widths = (36, 110, 240, 90, 55, 70, 90, 90, 45, 45,
                  80, 110, 50, 50, 90, 90, 50, 50)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, anchor="w",
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=w, anchor="w")

        self.tree.tag_configure("major_phase",
                                 background=C["steel"], foreground="white",
                                 font=F["small_b"])
        self.tree.tag_configure("sub_phase",
                                 background=C["steel_light"], foreground="#111111",
                                 font=F["small"])
        self.tree.tag_configure("tint_red",    background=C["red_light"])
        self.tree.tag_configure("tint_amber",  background=C["amber_row"])
        self.tree.tag_configure("tint_green",  background=C["green_light"])
        self.tree.tag_configure("tint_blue",   background=C["blue_light"])
        self.tree.tag_configure("row_alt",     background=C["row_alt"])

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._context_menu)

        self._rebuild_table()

    def _trace_search(self):
        def cb(*_a):
            self._rebuild_table()
        try:
            self.search_var.trace_add("write", lambda *_: cb())
        except AttributeError:
            self.search_var.trace("w", cb)

    def _rebuild_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        acts = list(self.app.activities)
        q = self.search_var.get().lower()

        filtered = [
            a for a in acts
            if (self.filter_phase == "All" or a["phase"] == self.filter_phase)
            and (self.filter_status == "All" or a["status"] == self.filter_status)
            and (self.filter_dept == "All" or a["dept"] == self.filter_dept)
            and (not q or q in (a["activity_name"] or "").lower())
        ]

        sort_key_map = {
            "#": lambda a: a.get("seq_num") or 0,
            "Phase": lambda a: (a.get("phase") or "", a.get("seq_num") or 0),
            "Activity": lambda a: (a.get("activity_name") or "").lower(),
            "Tech": lambda a: (a.get("technician") or "").lower(),
            "Dept": lambda a: a.get("dept") or "",
            "Priority": lambda a: a.get("priority") or "",
            "Plan Start": lambda a: a.get("plan_start") or "",
            "Plan Finish": lambda a: a.get("plan_finish") or "",
            "Dur": lambda a: int(a.get("duration_d") or 0),
            "Float": lambda a: int(a.get("float_d") or 0),
            "% Done": lambda a: int(a.get("pct_complete") or 0),
            "Status": lambda a: a.get("status") or "",
            "Est h": lambda a: float(a.get("est_hours") or 0),
            "Act h": lambda a: float(a.get("actual_hours") or 0),
            "Act Start": lambda a: a.get("actual_start") or "",
            "Act Finish": lambda a: a.get("actual_finish") or "",
            "Delay": lambda a: int(a.get("delay_d") or 0),
            "Alert": lambda a: a.get("alert_level") or "",
        }
        key_fn = sort_key_map.get(self.sort_col, sort_key_map["#"])
        filtered.sort(key=key_fn, reverse=self.sort_reverse)

        self.count_var.set(
            f"Showing {len(filtered)} of {len(acts)} activities")

        row_num = 0
        cur_major = None
        cur_phase = None

        for a in filtered:
            if a["major_phase"] != cur_major:
                cur_major = a["major_phase"]
                cur_phase = None
                total_m = sum(1 for x in acts if x["major_phase"] == cur_major)
                done_m = sum(1 for x in acts if x["major_phase"] == cur_major
                              and x["status"] == "Complete")
                label = f"  ⬛  {cur_major}    [{done_m}/{total_m} complete]"
                self.tree.insert("", "end",
                    values=(label, "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", ""),
                    tags=("major_phase",), iid=f"major_{cur_major}")

            if a["phase"] != cur_phase:
                cur_phase = a["phase"]
                total_p = sum(1 for x in acts if x["phase"] == cur_phase)
                done_p = sum(1 for x in acts if x["phase"] == cur_phase
                              and x["status"] == "Complete")
                label = f"     ▸  {cur_phase}    [{done_p}/{total_p}]"
                self.tree.insert("", "end",
                    values=(label, "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", ""),
                    tags=("sub_phase",), iid=f"phase_{cur_phase}")

            alert = a.get("alert_level", "OK")
            status = a["status"]
            if alert == "CRIT" or status in ("Blocked", "Delayed"):
                tag = "tint_red"
            elif alert == "WARN":
                tag = "tint_amber"
            elif status == "Complete":
                tag = "tint_green"
            elif status == "In Progress":
                tag = "tint_blue"
            elif row_num % 2 == 0:
                tag = "row_alt"
            else:
                tag = ""

            alert_disp = {"CRIT": "!! CRIT", "WARN": "! WARN", "OK": "✓"}.get(alert, "")
            pct_disp = f"{a['pct_complete']}%"

            self.tree.insert("", "end",
                iid=str(a["id"]),
                values=(
                    a["seq_num"], a["phase"], a["activity_name"],
                    a.get("technician", ""), a["dept"], a["priority"],
                    a.get("plan_start", ""), a.get("plan_finish", ""),
                    a.get("duration_d", ""), a.get("float_d", ""),
                    pct_disp, a["status"],
                    a.get("est_hours", ""), a.get("actual_hours", ""),
                    a.get("actual_start", ""), a.get("actual_finish", ""),
                    a.get("delay_d", ""), alert_disp,
                ),
                tags=(tag,)
            )
            row_num += 1

    def _on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id or not row_id.isdigit():
            return

        act_id = int(row_id)
        col_idx = int(col.replace("#", "")) - 1
        col_names = (
            "seq_num", "phase", "activity_name", "technician", "dept",
            "priority", "plan_start", "plan_finish", "duration_d", "float_d",
            "pct_complete", "status", "est_hours", "actual_hours",
            "actual_start", "actual_finish", "delay_d", "alert_level",
        )
        READONLY = {0, 7, 8, 9, 17}
        if col_idx in READONLY:
            return

        field = col_names[col_idx]
        act = db_fetchone("SELECT * FROM activities WHERE id=?", (act_id,))
        if not act:
            return

        self._inline_edit_dialog(act_id, field, act.get(field, ""))

    def _inline_edit_dialog(self, act_id: int, field: str, current_val):
        DROPDOWN_FIELDS = {
            "status":   self.app.config.get("status", []),
            "priority": self.app.config.get("priority", []),
            "dept":     self.app.config.get("department", []),
            "phase":    (self.app.config.get("phases_mech", []) +
                         self.app.config.get("phases_elec", [])),
        }

        dlg = tk.Toplevel(self.app.root)
        dlg.title(f"Edit — {field.replace('_', ' ').title()}")
        dlg.geometry("360x140")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg=C["card"])

        tk.Label(dlg, text=f"Edit: {field.replace('_', ' ').title()}",
                 font=F["h3"], bg=C["card"]).pack(padx=16, pady=(14, 6), anchor="w")

        var = tk.StringVar(value=str(current_val) if current_val is not None else "")

        if field in DROPDOWN_FIELDS:
            widget = ttk.Combobox(dlg, textvariable=var,
                                   values=DROPDOWN_FIELDS[field],
                                   state="readonly", width=36)
        elif field in ("pct_complete", "est_hours", "actual_hours", "hrs_spent"):
            widget = ttk.Spinbox(dlg, from_=0, to=9999, textvariable=var, width=36)
        else:
            widget = ttk.Entry(dlg, textvariable=var, width=36)

        widget.pack(padx=16, pady=(0, 12))
        widget.focus()

        def save():
            new_val = var.get()
            if field in ("pct_complete",):
                try:
                    new_val = max(0, min(100, int(float(new_val))))
                except ValueError:
                    messagebox.showerror("Invalid", "Must be a number 0–100")
                    return
            elif field in ("est_hours", "actual_hours"):
                try:
                    new_val = float(new_val)
                except ValueError:
                    messagebox.showerror("Invalid", "Must be a number")
                    return

            if field == "phase":
                from backend.models import MECH_PHASES
                major = ("MECHANICAL PREP" if new_val in MECH_PHASES
                         else "ELECTRICAL PREP")
                db_execute("""UPDATE activities
                    SET major_phase=?, phase=?, updated_at=datetime('now') WHERE id=?""",
                    (major, new_val, act_id))
            else:
                db_execute(f"""UPDATE activities
                    SET {field}=?, updated_at=datetime('now') WHERE id=?""",
                    (new_val, act_id))

            needs_schedule = field in ("est_hours",)
            needs_derived = field in ("status", "pct_complete", "actual_start",
                                       "actual_finish", "est_hours", "phase")
            if needs_schedule:
                run_schedule_and_save(self.app.active_project_id)
            elif needs_derived:
                proj = db_fetchone("SELECT * FROM projects WHERE id=?",
                                    (self.app.active_project_id,))
                acts = get_activities(self.app.active_project_id)
                acts = compute_derived(
                    acts, proj.get("target_finish", ""),
                    int(proj.get("warn_threshold") or 3),
                    int(proj.get("crit_threshold") or 1))
                from backend.database import get_conn
                conn = get_conn()
                for a in acts:
                    conn.execute("""UPDATE activities
                        SET float_d=?, delay_d=?, alert_level=?,
                            updated_at=datetime('now') WHERE id=?""",
                        (a["float_d"], a["delay_d"], a["alert_level"], a["id"]))
                conn.commit()
                conn.close()
                sync_delays(self.app.active_project_id)

            dlg.destroy()
            self.app.refresh()
            self.app.toast.show("Saved", f"{field} updated", "ok")

        btn_frame = tk.Frame(dlg, bg=C["card"])
        btn_frame.pack(pady=(0, 14), padx=16, anchor="e")
        ttk.Button(btn_frame, text="Cancel", style="Ghost.TButton",
                   command=dlg.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Save", style="Primary.TButton",
                   command=save).pack(side="left")

        dlg.bind("<Return>", lambda e: save())
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def _context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id or not row_id.isdigit():
            return
        act_id = int(row_id)
        self.tree.selection_set(row_id)

        menu = tk.Menu(self.app.root, tearoff=0)
        menu.add_command(label="Edit Status",
                         command=lambda: self._inline_edit_dialog(
                             act_id, "status",
                             db_fetchone("SELECT status FROM activities WHERE id=?",
                                         (act_id,))["status"]))
        menu.add_command(label="Edit % Complete",
                         command=lambda: self._inline_edit_dialog(
                             act_id, "pct_complete",
                             db_fetchone("SELECT pct_complete FROM activities WHERE id=?",
                                         (act_id,))["pct_complete"]))
        menu.add_command(label="Edit Technician",
                         command=lambda: self._inline_edit_dialog(
                             act_id, "technician",
                             db_fetchone("SELECT technician FROM activities WHERE id=?",
                                         (act_id,))["technician"]))
        menu.add_separator()
        menu.add_command(label="Delete Activity",
                         command=lambda: self._delete_activity(act_id))
        menu.post(event.x_root, event.y_root)

    def _add_activity_dialog(self):
        from ui.modules.project_switcher import FormDialog
        config = self.app.config
        fields = [
            ("Activity Name *", "name", "entry", None),
            ("Phase *", "phase", "combo",
             config.get("phases_mech", []) + config.get("phases_elec", [])),
            ("Technician", "technician", "entry", None),
            ("Department", "dept", "combo", config.get("department", [])),
            ("Priority", "priority", "combo", config.get("priority", [])),
            ("Est. Hours", "est_hours", "spinbox", None),
        ]
        defaults = {"est_hours": "9", "priority": "Medium", "dept": "Mech"}
        FormDialog(self.app.root, "Add Activity", fields, defaults,
                   self._do_add_activity)

    def _do_add_activity(self, data: dict):
        from backend.models import MECH_PHASES
        major = ("MECHANICAL PREP" if data.get("phase") in MECH_PHASES
                 else "ELECTRICAL PREP")
        acts = get_activities(self.app.active_project_id)
        next_seq = max((a["seq_num"] for a in acts), default=0) + 1
        try:
            est = float(data.get("est_hours", 9))
        except (TypeError, ValueError):
            est = 9.0
        db_execute("""INSERT INTO activities
            (project_id, seq_num, major_phase, phase, activity_name,
             technician, dept, priority, pct_complete, status, est_hours)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (self.app.active_project_id, next_seq, major,
             data.get("phase", ""), data.get("name", ""),
             data.get("technician", ""), data.get("dept", "Mech"),
             data.get("priority", "Medium"), 0, "Not Started", est))
        run_schedule_and_save(self.app.active_project_id)
        self.app.refresh()
        self.app.toast.show("Added", "New activity created and scheduled", "ok")

    def _delete_activity(self, act_id: int):
        if not messagebox.askyesno("Delete Activity",
                                    "Delete this activity? This cannot be undone."):
            return
        db_execute("DELETE FROM activities WHERE id=?", (act_id,))
        acts = get_activities(self.app.active_project_id)
        from backend.database import get_conn
        conn = get_conn()
        for i, a in enumerate(acts, 1):
            conn.execute("UPDATE activities SET seq_num=? WHERE id=?", (i, a["id"]))
        conn.commit()
        conn.close()
        run_schedule_and_save(self.app.active_project_id)
        self.app.refresh()
        self.app.toast.show("Deleted", "Activity removed", "warn")

    def _run_auto_schedule(self):
        run_schedule_and_save(self.app.active_project_id)
        self.app.refresh()
        self.app.toast.show("Auto-Schedule Complete",
                            f"{len(self.app.activities)} activities updated", "ok")

    def _export_excel(self):
        from ui.modules.reports import export_activities
        export_activities(self.app)

    def _filter_change(self, key: str, val: str):
        if key == "phase":
            self.filter_phase = val
        elif key == "status":
            self.filter_status = val
        elif key == "dept":
            self.filter_dept = val
        self._rebuild_table()

    def _sort(self, col: str):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self._rebuild_table()

    def _card_border(self, f):
        f.configure(highlightbackground=C["border"], highlightthickness=1)
