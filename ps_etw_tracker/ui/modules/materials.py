import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import C, F
from backend.database import db_execute, db_fetchone


class MaterialsModule:
    COLS = (
        "#", "Part #", "Description", "Linked Act", "Qty", "Owner",
        "Crit.", "Need-By", "Status", "Supplier", "Tracking",
        "Promised", "Received", "Risk", "Lead(d)", "Value €",
        "Notes", "Latest Order", "Alert",
    )

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.sort_col = "#"
        self.sort_reverse = False

    def render(self):
        mats = self.app.materials
        total = len(mats)
        not_ord = sum(1 for m in mats if m.get("status") == "Not Ordered")
        transit = sum(1 for m in mats if m.get("status") == "In Transit")
        avail = sum(1 for m in mats if m.get("status") == "Available")
        at_risk = sum(1 for m in mats if m.get("risk_flag") == "AT RISK")
        crit = sum(1 for m in mats if m.get("criticality") == "Critical")

        strip = tk.Frame(self.parent, bg=C["bg"])
        strip.pack(fill="x", pady=(0, 12))
        kpi_data = [
            ("TOTAL PARTS", str(total), "line items", C["steel"]),
            ("NOT ORDERED", str(not_ord), "items", C["red"]),
            ("IN TRANSIT", str(transit), "items", C["blue_mid"]),
            ("AVAILABLE", str(avail), "items", C["green"]),
            ("AT RISK", str(at_risk), "flagged", C["amber"]),
            ("CRITICAL", str(crit), "items", C["red_dark"]),
        ]
        for i, (lab, val, sub, bc) in enumerate(kpi_data):
            card = tk.Frame(strip, bg=C["card"], padx=12, pady=12)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            strip.grid_columnconfigure(i, weight=1)
            tk.Frame(card, width=4, bg=bc).pack(side="left", fill="y", padx=(0, 8))
            inner = tk.Frame(card, bg=C["card"])
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=lab, font=F["caption"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            tk.Label(inner, text=val, font=F["kpi_sm"], bg=C["card"], fg="#000").pack(anchor="w")
            tk.Label(inner, text=sub, font=F["small"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            card.configure(highlightbackground=C["border"], highlightthickness=1)

        toolbar = tk.Frame(self.parent, bg=C["card"], padx=12, pady=8)
        toolbar.pack(fill="x", pady=(0, 8))
        toolbar.configure(highlightbackground=C["border"], highlightthickness=1)

        ttk.Button(toolbar, text="+ Add Part", style="Primary.TButton",
                   command=self._add_part).pack(side="right", padx=(6, 0))
        ttk.Button(toolbar, text="⬇ Export", style="Secondary.TButton",
                   command=self._export).pack(side="right")
        ttk.Button(toolbar, text="⟳ Refresh", style="Ghost.TButton",
                   command=lambda: self.app.refresh()).pack(side="left")

        tbl_frame = tk.Frame(self.parent, bg=C["card"])
        tbl_frame.pack(fill="both", expand=True)
        tbl_frame.configure(highlightbackground=C["border"], highlightthickness=1)

        self.tree = ttk.Treeview(tbl_frame, columns=self.COLS, show="headings", selectmode="browse")
        widths = (40, 90, 200, 70, 45, 70, 55, 85, 100, 90, 80, 75, 75, 60, 50, 55, 120, 85, 100)
        for col, w in zip(self.COLS, widths):
            self.tree.heading(col, text=col, anchor="w",
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=40, anchor="w")

        self.tree.tag_configure("tint_red", background=C["red_light"])
        self.tree.tag_configure("tint_blue", background=C["blue_light"])
        self.tree.tag_configure("tint_green", background=C["green_light"])
        self.tree.tag_configure("tint_amber", background=C["amber_light"])
        self.tree.tag_configure("order_alert", foreground=C["red_dark"])

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Button-3>", self._context_menu)

        self._populate()

    def _populate(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        mats = list(self.app.materials)
        sort_map = {
            "#": lambda m: m.get("id") or 0,
            "Part #": lambda m: (m.get("part_number") or "").lower(),
            "Description": lambda m: (m.get("description") or "").lower(),
            "Linked Act": lambda m: int(m.get("linked_activity_id") or 0),
            "Qty": lambda m: int(m.get("quantity") or 0),
            "Owner": lambda m: m.get("ownership") or "",
            "Crit.": lambda m: m.get("criticality") or "",
            "Need-By": lambda m: m.get("need_by_date") or "",
            "Status": lambda m: m.get("status") or "",
            "Supplier": lambda m: (m.get("supplier") or "").lower(),
            "Tracking": lambda m: m.get("tracking_ref") or "",
            "Promised": lambda m: m.get("promised_date") or "",
            "Received": lambda m: m.get("received_date") or "",
            "Risk": lambda m: m.get("risk_flag") or "",
            "Lead(d)": lambda m: int(m.get("lead_time_d") or 0),
            "Value €": lambda m: float(m.get("value_eur") or 0),
            "Notes": lambda m: (m.get("notes") or "").lower(),
            "Latest Order": lambda m: m.get("latest_order_date") or "",
            "Alert": lambda m: m.get("order_alert") or "",
        }
        key_fn = sort_map.get(self.sort_col, sort_map["#"])
        mats.sort(key=key_fn, reverse=self.sort_reverse)

        for m in mats:
            st = m.get("status") or ""
            if st == "Not Ordered":
                tag = "tint_red"
            elif st == "In Transit":
                tag = "tint_blue"
            elif st in ("Available", "Arrived"):
                tag = "tint_green"
            else:
                tag = "tint_amber"
            oa = str(m.get("order_alert") or "")
            tags = (tag,)
            if oa.startswith("ORDER NOW"):
                tags = (tag, "order_alert")

            self.tree.insert("", "end", iid=str(m["id"]), tags=tags, values=(
                m["id"],
                m.get("part_number", ""),
                m.get("description", ""),
                m.get("linked_activity_id", "") or "",
                m.get("quantity", ""),
                m.get("ownership", ""),
                m.get("criticality", ""),
                m.get("need_by_date", ""),
                m.get("status", ""),
                m.get("supplier", ""),
                m.get("tracking_ref", ""),
                m.get("promised_date", ""),
                m.get("received_date", ""),
                m.get("risk_flag", ""),
                m.get("lead_time_d", ""),
                m.get("value_eur", ""),
                (m.get("notes", "") or "")[:40],
                m.get("latest_order_date", ""),
                oa[:40] if oa else "—",
            ))

    def _sort(self, col: str):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self._populate()

    def _context_menu(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        mid = int(row)
        self.tree.selection_set(row)
        menu = tk.Menu(self.app.root, tearoff=0)
        menu.add_command(label="Edit Status",
                         command=lambda: self._edit_field(mid, "status", "combo",
                             self.app.config.get("mat_status", [])))
        menu.add_command(label="Edit Risk Flag",
                         command=lambda: self._edit_risk(mid))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self._delete(mid))
        menu.post(event.x_root, event.y_root)

    def _edit_risk(self, mid: int):
        dlg = tk.Toplevel(self.app.root)
        dlg.title("Risk Flag")
        dlg.geometry("320x120")
        dlg.grab_set()
        dlg.configure(bg=C["card"])
        var = tk.StringVar(value=db_fetchone(
            "SELECT risk_flag FROM materials WHERE id=?", (mid,))["risk_flag"])
        vals = ["OK", "WARN", "AT RISK"]
        ttk.Combobox(dlg, textvariable=var, values=vals, state="readonly").pack(padx=16, pady=16)

        def save():
            db_execute("UPDATE materials SET risk_flag=? WHERE id=?", (var.get(), mid))
            dlg.destroy()
            self.app.refresh()
            self.app.toast.show("Saved", "Risk flag updated", "ok")

        ttk.Button(dlg, text="Save", style="Primary.TButton", command=save).pack()

    def _edit_field(self, mid: int, field: str, kind: str, options=None):
        cur = db_fetchone(f"SELECT {field} FROM materials WHERE id=?", (mid,))
        if not cur:
            return
        dlg = tk.Toplevel(self.app.root)
        dlg.title(field)
        dlg.geometry("360x120")
        dlg.grab_set()
        dlg.configure(bg=C["card"])
        var = tk.StringVar(value=str(cur[field]))

        if kind == "combo":
            ttk.Combobox(dlg, textvariable=var, values=options or [], state="readonly").pack(
                padx=16, pady=16, fill="x")
        else:
            ttk.Entry(dlg, textvariable=var).pack(padx=16, pady=16, fill="x")

        def save():
            db_execute(f"UPDATE materials SET {field}=? WHERE id=?", (var.get(), mid))
            dlg.destroy()
            self.app.refresh()
            self.app.toast.show("Saved", field + " updated", "ok")

        ttk.Button(dlg, text="Save", style="Primary.TButton", command=save).pack()

    def _delete(self, mid: int):
        if not messagebox.askyesno("Delete", "Remove this material line?"):
            return
        db_execute("DELETE FROM materials WHERE id=?", (mid,))
        self.app.refresh()
        self.app.toast.show("Deleted", "Material removed", "warn")

    def _add_part(self):
        from ui.modules.project_switcher import FormDialog
        cfg = self.app.config
        fields = [
            ("Description *", "description", "entry", None),
            ("Part Number", "part_number", "entry", None),
            ("Quantity", "quantity", "spinbox", None),
            ("Linked Activity ID", "linked_activity_id", "entry", None),
            ("Ownership", "ownership", "combo", cfg.get("ownership", [])),
            ("Criticality", "criticality", "combo", cfg.get("criticality", [])),
            ("Need-By Date", "need_by_date", "entry", None),
            ("Status", "status", "combo", cfg.get("mat_status", [])),
            ("Supplier", "supplier", "entry", None),
            ("Lead Time (days)", "lead_time_d", "spinbox", None),
            ("Value (EUR)", "value_eur", "entry", None),
        ]
        defaults = {"quantity": "1", "status": "Not Ordered", "ownership": "Bosch",
                    "criticality": "Medium"}
        FormDialog(self.app.root, "Add Part", fields, defaults, self._do_add)

    def _do_add(self, data: dict):
        try:
            qty = int(data.get("quantity") or 1)
        except ValueError:
            qty = 1
        try:
            linked = int(data.get("linked_activity_id") or 0) or None
        except ValueError:
            linked = None
        try:
            lead = int(data.get("lead_time_d") or 0)
        except ValueError:
            lead = 0
        try:
            val = float(data.get("value_eur") or 0)
        except ValueError:
            val = 0.0
        db_execute("""INSERT INTO materials
            (project_id, part_number, description, linked_activity_id, quantity,
             ownership, criticality, need_by_date, status, supplier, lead_time_d, value_eur)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.app.active_project_id,
             data.get("part_number", ""),
             data.get("description", ""),
             linked, qty,
             data.get("ownership", "Bosch"),
             data.get("criticality", "Medium"),
             data.get("need_by_date", ""),
             data.get("status", "Not Ordered"),
             data.get("supplier", ""),
             lead, val))
        self.app.refresh()
        self.app.toast.show("Added", "Material saved", "ok")

    def _export(self):
        from ui.modules.reports import export_materials
        export_materials(self.app)
