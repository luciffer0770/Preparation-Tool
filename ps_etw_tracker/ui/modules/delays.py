import tkinter as tk
from tkinter import ttk
from ui.theme import C, F
from backend.database import db_execute, db_fetchone
from backend.scheduler import parse_date


class DelaysModule:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.selected_delay_id: int | None = None

    def render(self):
        dels = self.app.delays
        open_ct = sum(1 for d in dels if d.get("delay_status") == "Open")
        mit = sum(1 for d in dels if d.get("delay_status") == "Mitigating")
        open_actions = sum(
            1 for d in dels if d.get("delay_status") in ("Open", "Mitigating"))
        total_hrs = sum(float(d.get("total_delay_hrs") or 0) for d in dels)
        overdue = 0
        from datetime import date
        today = date.today()
        for d in dels:
            td = parse_date(d.get("target_date") or "")
            if td and td < today and d.get("delay_status") != "Closed":
                overdue += 1

        strip = tk.Frame(self.parent, bg=C["bg"])
        strip.pack(fill="x", pady=(0, 12))
        items = [
            ("OPEN DELAYS", str(open_ct), "status=Open", C["amber"]),
            ("MITIGATING", str(mit), "in progress", C["blue_mid"]),
            ("TOTAL DELAY HRS", f"{total_hrs:.1f}", "logged hours", C["red"]),
            ("OPEN ACTIONS", str(open_actions), "open + mitigating", C["steel"]),
            ("OVERDUE ACTIONS", str(overdue), "past target", C["red_dark"]),
        ]
        for i, (a, b, c, col) in enumerate(items):
            card = tk.Frame(strip, bg=C["card"], padx=12, pady=10)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            strip.grid_columnconfigure(i, weight=1)
            tk.Frame(card, width=4, bg=col).pack(side="left", fill="y", padx=(0, 8))
            inner = tk.Frame(card, bg=C["card"])
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=a, font=F["caption"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            tk.Label(inner, text=b, font=F["kpi_sm"], bg=C["card"]).pack(anchor="w")
            tk.Label(inner, text=c, font=F["small"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            card.configure(highlightbackground=C["border"], highlightthickness=1)

        split = tk.Frame(self.parent, bg=C["bg"])
        split.pack(fill="both", expand=True)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)

        left = tk.Frame(split, bg=C["card"])
        left.grid(row=0, column=0, sticky="nsew")
        left.configure(highlightbackground=C["border"], highlightthickness=1)

        cols = ("Activity", "Phase", "Owner", "Plan Start", "Plan Finish", "Float", "%", "Status")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=14)
        wds = (220, 100, 90, 90, 90, 50, 40, 80)
        for c, w in zip(cols, wds):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        vsb = ttk.Scrollbar(left, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        for d in dels:
            self.tree.insert("", "end", iid=str(d["id"]), values=(
                d.get("activity_name", ""),
                d.get("phase", ""),
                d.get("technician", ""),
                d.get("plan_start", ""),
                d.get("plan_finish", ""),
                d.get("float_d", ""),
                f"{d.get('pct_complete', 0)}%",
                d.get("act_status", ""),
            ))

        detail = tk.Frame(split, bg=C["card"], width=420)
        detail.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        detail.grid_propagate(True)
        detail.configure(highlightbackground=C["border"], highlightthickness=1)

        tk.Label(detail, text="Delay action (auto-saves)", font=F["h3"],
                 bg=C["card"]).pack(anchor="w", padx=12, pady=(12, 8))

        self.detail_inner = tk.Frame(detail, bg=C["card"], padx=12)
        self.detail_inner.pack(fill="both", expand=True)

        self._clear_detail()

    def _clear_detail(self):
        for w in self.detail_inner.winfo_children():
            w.destroy()
        tk.Label(self.detail_inner, text="Select a delay row to edit",
                 font=F["small"], bg=C["card"], fg=C["muted"]).pack(pady=20)

    def _on_select(self, _e=None):
        sel = self.tree.selection()
        if not sel:
            self.selected_delay_id = None
            self._clear_detail()
            return
        did = int(sel[0])
        self.selected_delay_id = did
        row = db_fetchone("SELECT * FROM delays_actions WHERE id=?", (did,))
        if not row:
            return
        for w in self.detail_inner.winfo_children():
            w.destroy()

        cfg = self.app.config

        def row_combo(label, field, values, key):
            f = tk.Frame(self.detail_inner, bg=C["card"])
            f.pack(fill="x", pady=4)
            tk.Label(f, text=label, font=F["caption"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            var = tk.StringVar(value=row.get(key) or "")
            cb = ttk.Combobox(f, textvariable=var, values=values, state="readonly")
            cb.pack(fill="x")

            def save(*_a):
                db_execute(
                    f"UPDATE delays_actions SET {field}=?, updated_at=datetime('now') WHERE id=?",
                    (var.get(), did))
                self.app.refresh()
                self.app.toast.show("Saved", label.strip(), "ok")

            cb.bind("<<ComboboxSelected>>", save)

        def row_entry(label, field, key):
            f = tk.Frame(self.detail_inner, bg=C["card"])
            f.pack(fill="x", pady=4)
            tk.Label(f, text=label, font=F["caption"], bg=C["card"], fg=C["muted"]).pack(anchor="w")
            var = tk.StringVar(value=str(row.get(key) or ""))
            ent = ttk.Entry(f, textvariable=var)
            ent.pack(fill="x")

            def save(_e=None):
                db_execute(
                    f"UPDATE delays_actions SET {field}=?, updated_at=datetime('now') WHERE id=?",
                    (var.get(), did))
                self.app.refresh()
                self.app.toast.show("Saved", label.strip(), "ok")

            ent.bind("<FocusOut>", save)

        row_combo("Root cause", "root_cause", cfg.get("root_cause", []), "root_cause")
        row_entry("Action required", "action_required", "action_required")
        row_entry("Action owner", "action_owner", "action_owner")
        row_entry("Target date", "target_date", "target_date")
        row_combo("Delay status", "delay_status", cfg.get("action_status", []), "delay_status")

        tk.Label(self.detail_inner, text="Resolution", font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(8, 0))
        txt = tk.Text(self.detail_inner, height=5, width=40, font=F["small"],
                      bg=C["card"], relief="solid", bd=1)
        txt.insert("1.0", row.get("resolution") or "")
        txt.pack(fill="x")

        def save_res(_e=None):
            body = txt.get("1.0", "end-1c")
            db_execute(
                "UPDATE delays_actions SET resolution=?, updated_at=datetime('now') WHERE id=?",
                (body, did))
            self.app.refresh()
            self.app.toast.show("Saved", "Resolution", "ok")

        txt.bind("<FocusOut>", save_res)
