import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import C, F
from backend.database import get_projects, db_execute, db_fetchone
from backend.models import create_project_with_activities


class ProjectSwitcherDrawer:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("")
        self.win.resizable(False, False)
        self.win.geometry(f"380x{app.root.winfo_height()}+{app.root.winfo_x()}+{app.root.winfo_y() + 50}")
        self.win.configure(bg=C["card"])
        self.win.grab_set()
        self.search_var = tk.StringVar()
        self._build()

    def _build(self):
        hdr = tk.Frame(self.win, bg=C["card"], padx=14, pady=12)
        hdr.pack(fill="x")
        tk.Frame(self.win, height=2, bg=C["red"]).pack(fill="x")
        tk.Label(hdr, text="All Projects", font=F["h2"],
                 bg=C["card"], fg="#111111").pack(side="left")
        ttk.Button(hdr, text="+ New", style="Primary.TButton",
                   command=self._new_project).pack(side="right", padx=(6, 0))
        ttk.Button(hdr, text="✕", style="Ghost.TButton",
                   command=self.win.destroy).pack(side="right")

        search_f = tk.Frame(self.win, bg=C["card"], padx=12, pady=6)
        search_f.pack(fill="x")
        ttk.Entry(search_f, textvariable=self.search_var,
                  font=F["small"]).pack(fill="x")
        try:
            self.search_var.trace_add("write", lambda *_: self._refresh_list())
        except AttributeError:
            self.search_var.trace("w", lambda *_: self._refresh_list())

        list_container = tk.Frame(self.win, bg=C["card"])
        list_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(list_container, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.list_frame = tk.Frame(canvas, bg=C["card"])
        self.list_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        def _mw(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", _mw)

        self.canvas = canvas
        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        q = self.search_var.get().lower()
        projects = get_projects()
        filtered = [p for p in projects
                    if not q or q in p["code"].lower() or q in (p["name"] or "").lower()]
        for p in filtered:
            self._project_card(p)

    def _project_card(self, p: dict):
        is_active = (p["id"] == self.app.active_project_id)
        bg = C["card"]
        border_c = C["red"] if is_active else C["border"]

        card = tk.Frame(self.list_frame, bg=bg, padx=12, pady=10,
                        highlightbackground=border_c, highlightthickness=2 if is_active else 1,
                        cursor="hand2")
        card.pack(fill="x", padx=8, pady=(0, 6))

        r1 = tk.Frame(card, bg=bg)
        r1.pack(fill="x")
        tk.Label(r1, text=p["code"], font=F["mono"],
                 bg=bg, fg=C["red"]).pack(side="left")
        tk.Label(r1, text=f"  {p['name']}", font=F["body_b"],
                 bg=bg, fg="#111111").pack(side="left")

        tk.Label(card, text=p.get("customer", ""), font=F["small"],
                 bg=bg, fg=C["muted"]).pack(anchor="w")

        bar_outer = tk.Frame(card, bg=C["border"], height=4)
        bar_outer.pack(fill="x", pady=(4, 0))
        pct = p.get("pct", 0)
        bar_fill = tk.Frame(bar_outer, bg=C["red"], height=4)
        bar_fill.place(relwidth=pct / 100, relheight=1)

        r3 = tk.Frame(card, bg=bg)
        r3.pack(fill="x", pady=(4, 0))
        tk.Label(r3, text=f"Status: {p['status']}  |  {pct}% complete",
                 font=F["small"], bg=bg, fg=C["text"]).pack(side="left")

        def select(pid=p["id"]):
            self.win.destroy()
            self.app.select_project(pid)
        card.bind("<Button-1>", lambda e: select())
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: select())

    def _new_project(self):
        self.win.destroy()
        NewProjectDialog(self.app)


class NewProjectDialog:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("New Project")
        self.win.geometry("640x580")
        self.win.resizable(False, False)
        self.win.configure(bg=C["card"])
        self.win.grab_set()
        self.vars = {}
        self._build()

    def _field(self, parent, label, key, default="", is_num=False):
        frame = tk.Frame(parent, bg=C["card"])
        frame.pack(fill="x", pady=(0, 8))
        tk.Label(frame, text=label.upper(), font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w")
        var = tk.StringVar(value=default)
        self.vars[key] = var
        if is_num:
            ttk.Spinbox(frame, from_=0, to=999, textvariable=var,
                        width=30, font=F["body"]).pack(fill="x")
        else:
            ttk.Entry(frame, textvariable=var, font=F["body"]).pack(fill="x")

    def _build(self):
        hdr = tk.Frame(self.win, bg=C["card"], padx=18, pady=14)
        hdr.pack(fill="x")
        tk.Frame(self.win, height=2, bg=C["red"]).pack(fill="x")
        tk.Label(hdr, text="New Project", font=F["h2"],
                 bg=C["card"], fg="#111111").pack(side="left")
        ttk.Button(hdr, text="✕", style="Ghost.TButton",
                   command=self.win.destroy).pack(side="right")

        canvas = tk.Canvas(self.win, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["card"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.itemconfig(cw, width=e.width)
        canvas.bind("<Configure>", _resize)

        body = tk.Frame(inner, bg=C["card"], padx=18, pady=12)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=C["card"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(body, bg=C["card"])
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="PROJECT INFORMATION", font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(0, 6))
        tk.Frame(left, height=1, bg=C["border"]).pack(fill="x", pady=(0, 8))

        self._field(left, "Project Code *", "code", "PRJ-005")
        self._field(left, "Project Name *", "name")
        self._field(left, "Customer / OEM", "customer")
        self._field(left, "Engine Type", "engine_type")
        self._field(left, "Engine Serial No.", "serial")
        self._field(left, "Trolley Code", "trolley_code")
        self._field(left, "Trolley Location", "trolley_location", "Bay 3 — Line A")
        self._field(left, "Project Manager", "pm_name")

        tk.Label(right, text="SCHEDULE", font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(0, 6))
        tk.Frame(right, height=1, bg=C["border"]).pack(fill="x", pady=(0, 8))
        self._field(right, "Planned Start Date *", "start_date", "16-Mar-26")
        self._field(right, "Target Finish Date *", "target_finish", "15-May-26")
        self._field(right, "Contract Reference", "contract_ref")
        self._field(right, "Working Hours/Day", "working_hrs", "9", is_num=True)
        self._field(right, "Warning Threshold (days)", "warn", "3", is_num=True)
        self._field(right, "Critical Threshold (days)", "crit", "1", is_num=True)

        info = tk.Frame(body, bg="#FAFAFA", padx=12, pady=10)
        info.configure(highlightbackground=C["border"], highlightthickness=1)
        info.pack(fill="x", pady=(12, 0))
        tk.Label(info, text=(
            "✓  Will instantiate 91 default activities from PS-ETW master template\n"
            "✓  Will run auto-schedule (9hr/day, Mon–Fri) on Planned Start\n"
            "✓  Will create empty Materials, Delays, Documents registers"
        ), font=F["small"], bg="#FAFAFA", fg=C["text"], justify="left").pack(anchor="w")

        footer = tk.Frame(self.win, bg=C["card"], padx=18, pady=12)
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, height=1, bg=C["border"]).pack(fill="x", pady=(0, 10))
        ttk.Button(footer, text="Cancel", style="Secondary.TButton",
                   command=self.win.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Create Project →", style="Primary.TButton",
                   command=self._create).pack(side="right")

    def _create(self):
        data = {k: v.get() for k, v in self.vars.items()}
        if not data.get("code") or not data.get("name"):
            messagebox.showwarning("Required Fields",
                "Project Code and Project Name are required.")
            return
        existing = db_fetchone("SELECT id FROM projects WHERE id=?", (data["code"],))
        if existing:
            messagebox.showerror("Duplicate Code",
                f"Project code '{data['code']}' already exists.")
            return
        try:
            proj_id = create_project_with_activities(data)
            self.win.destroy()
            self.app.select_project(proj_id)
            self.app.toast.show("Project Created",
                f"{data['code']} — {data['name']} with 91 activities", "ok")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class ProjectEditDialog:
    def __init__(self, app, proj: dict):
        self.app = app
        self.proj = proj
        self.win = tk.Toplevel(app.root)
        self.win.title(f"Edit Project — {proj['code']}")
        self.win.geometry("500x520")
        self.win.configure(bg=C["card"])
        self.win.grab_set()
        self.vars = {}
        self._build()

    def _field(self, parent, label, key):
        tk.Label(parent, text=label.upper(), font=F["caption"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(6, 0))
        var = tk.StringVar(value=self.proj.get(key, ""))
        self.vars[key] = var
        ttk.Entry(parent, textvariable=var, font=F["body"]).pack(fill="x")

    def _build(self):
        hdr = tk.Frame(self.win, bg=C["card"], padx=18, pady=12)
        hdr.pack(fill="x")
        tk.Frame(self.win, height=2, bg=C["red"]).pack(fill="x")
        tk.Label(hdr, text=f"Edit — {self.proj['code']}",
                 font=F["h2"], bg=C["card"]).pack(side="left")
        ttk.Button(hdr, text="✕", style="Ghost.TButton",
                   command=self.win.destroy).pack(side="right")

        body = tk.Frame(self.win, bg=C["card"], padx=18, pady=12)
        body.pack(fill="both", expand=True)

        for label, key in [
            ("Project Name", "name"), ("Customer / OEM", "customer"),
            ("Engine Type", "engine_type"), ("Engine Serial", "serial"),
            ("Trolley Code", "trolley_code"), ("Trolley Location", "trolley_location"),
            ("Project Manager", "pm_name"), ("Planned Start Date", "start_date"),
            ("Target Finish Date", "target_finish"), ("Contract Reference", "contract_ref"),
        ]:
            self._field(body, label, key)

        footer = tk.Frame(self.win, bg=C["card"], padx=18, pady=10)
        footer.pack(fill="x", side="bottom")
        ttk.Button(footer, text="Cancel", style="Ghost.TButton",
                   command=self.win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(footer, text="Save Changes", style="Primary.TButton",
                   command=self._save).pack(side="right")

    def _save(self):
        from backend.scheduler import run_schedule_and_save
        data = {k: v.get() for k, v in self.vars.items()}
        old_start = self.proj.get("start_date", "")
        set_clause = ", ".join(f"{k}=?" for k in data)
        vals = list(data.values()) + [self.proj["id"]]
        db_execute(f"UPDATE projects SET {set_clause}, updated_at=datetime('now') WHERE id=?",
                   vals)
        if data.get("start_date") != old_start:
            run_schedule_and_save(self.proj["id"])
        self.win.destroy()
        self.app.refresh()
        self.app.toast.show("Saved", "Project updated", "ok")


class FormDialog:
    def __init__(self, root, title, fields, defaults, on_submit):
        self.win = tk.Toplevel(root)
        self.win.title(title)
        self.win.configure(bg=C["card"])
        self.win.grab_set()
        self.vars = {}
        self.fields = fields
        self.on_submit = on_submit

        tk.Label(self.win, text=title, font=F["h2"],
                 bg=C["card"]).pack(padx=18, pady=(14, 0), anchor="w")
        tk.Frame(self.win, height=1, bg=C["border"]).pack(fill="x", padx=18, pady=8)

        body = tk.Frame(self.win, bg=C["card"], padx=18)
        body.pack(fill="both", expand=True)

        for label, key, ftype, options in fields:
            tk.Label(body, text=label.upper(), font=F["caption"],
                     bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(6, 0))
            var = tk.StringVar(value=defaults.get(key, ""))
            self.vars[key] = var
            if ftype == "combo":
                ttk.Combobox(body, textvariable=var, values=options or [],
                             state="readonly", font=F["body"]).pack(fill="x")
            elif ftype == "spinbox":
                ttk.Spinbox(body, from_=0, to=9999, textvariable=var,
                            font=F["body"]).pack(fill="x")
            else:
                ttk.Entry(body, textvariable=var, font=F["body"]).pack(fill="x")

        footer = tk.Frame(self.win, bg=C["card"], padx=18, pady=12)
        footer.pack(fill="x")
        ttk.Button(footer, text="Cancel", style="Ghost.TButton",
                   command=self.win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(footer, text="Create", style="Primary.TButton",
                   command=self._submit).pack(side="right")
        self.win.geometry("400x" + str(60 + len(fields) * 56))

    def _submit(self):
        data = {k: v.get() for k, v in self.vars.items()}
        self.win.destroy()
        self.on_submit(data)
