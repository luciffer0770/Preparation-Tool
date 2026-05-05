import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import C, F
from backend.database import get_projects, db_execute


class AllProjectsModule:
    COLS = ("Code", "Name", "Customer", "Engine", "PM", "Progress", "Status", "Target", "Health")

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

    def render(self):
        bar = tk.Frame(self.parent, bg=C["bg"])
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="+ New Project", style="Primary.TButton",
                   command=self._new_proj).pack(side="right")
        ttk.Button(bar, text="⟳ Refresh", style="Ghost.TButton",
                   command=lambda: self.app.refresh()).pack(side="left")

        tbl = tk.Frame(self.parent, bg=C["card"])
        tbl.pack(fill="both", expand=True)
        tbl.configure(highlightbackground=C["border"], highlightthickness=1)

        self.tree = ttk.Treeview(tbl, columns=self.COLS, show="headings", selectmode="browse")
        widths = (90, 180, 120, 100, 100, 70, 100, 100, 100)
        for c, w in zip(self.COLS, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)

        vsb = ttk.Scrollbar(tbl, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_dbl)

        btn_row = tk.Frame(self.parent, bg=C["bg"])
        btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_row, text="Archive", style="Secondary.TButton",
                   command=self._archive).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Delete", style="Danger.TButton",
                   command=self._delete).pack(side="left")

        self._populate()

    def _populate(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in get_projects():
            hid = "⚠ Overdue" if p.get("health") == "overdue" else "✓ On Schedule"
            code = p["code"]
            if p.get("archived"):
                code = f"[ARC] {code}"
            self.tree.insert("", "end", iid=p["id"], values=(
                code,
                p.get("name", ""),
                p.get("customer", ""),
                p.get("engine_type", ""),
                p.get("pm_name", ""),
                f"{p.get('pct', 0)}%",
                p.get("status", ""),
                p.get("target_finish", "") or "—",
                hid,
            ))

    def _sel_id(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _on_dbl(self, _e):
        pid = self._sel_id()
        if pid:
            self.app.select_project(pid)

    def _new_proj(self):
        from ui.modules.project_switcher import NewProjectDialog
        NewProjectDialog(self.app)

    def _archive(self):
        pid = self._sel_id()
        if not pid:
            return
        db_execute("UPDATE projects SET archived=1, updated_at=datetime('now') WHERE id=?",
                   (pid,))
        self.app.refresh()
        self.app.toast.show("Archived", pid, "ok")

    def _delete(self):
        pid = self._sel_id()
        if not pid:
            return
        if not messagebox.askyesno("Delete Project",
                                   f"Permanently delete project {pid} and all related data?"):
            return
        db_execute("DELETE FROM projects WHERE id=?", (pid,))
        if self.app.active_project_id == pid:
            self.app.active_project_id = None
        self.app.refresh()
        self.app.toast.show("Deleted", pid, "warn")
