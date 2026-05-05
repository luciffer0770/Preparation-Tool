import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import C, F
from backend.database import get_config, db_execute, db_fetchone


LIST_NAMES = [
    "status", "priority", "department", "ownership", "mat_status",
    "root_cause", "action_status", "criticality", "doc_type", "doc_category",
    "doc_status", "phases_mech", "phases_elec",
]


class SettingsModule:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

    def render(self):
        tk.Label(self.parent, text="Configuration Lists",
                 font=F["h2"], bg=C["bg"]).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(self.parent, bg=C["bg"])
        grid.pack(fill="both", expand=True)

        for i, name in enumerate(LIST_NAMES):
            col = i % 3
            row = i // 3
            self._list_editor(grid, name, row, col)

    def _list_editor(self, parent, list_name, row, col):
        box = tk.Frame(parent, bg=C["card"], padx=10, pady=10)
        box.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        box.configure(highlightbackground=C["border"], highlightthickness=1)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(box, text=list_name.replace("_", " ").title(),
                 font=F["h3"], bg=C["card"]).pack(anchor="w", pady=(0, 6))

        lb = tk.Listbox(box, height=8, font=F["small"], activestyle="none")
        lb.pack(fill="both", expand=True)

        add_f = tk.Frame(box, bg=C["card"])
        add_f.pack(fill="x", pady=(6, 0))
        var = tk.StringVar()
        ttk.Entry(add_f, textvariable=var).pack(side="left", fill="x", expand=True, padx=(0, 6))

        def refresh():
            lb.delete(0, tk.END)
            cfg = get_config()
            for v in cfg.get(list_name, []):
                lb.insert(tk.END, v)

        def add_val():
            val = var.get().strip()
            if not val:
                return
            try:
                r = db_fetchone(
                    "SELECT COALESCE(MAX(sort_order),-1)+1 AS n FROM config_lists WHERE list_name=?",
                    (list_name,))
                next_ord = int(r["n"]) if r else 0
                db_execute(
                    "INSERT INTO config_lists(list_name,list_value,sort_order) VALUES(?,?,?)",
                    (list_name, val, next_ord))
                var.set("")
                self.app.config = get_config()
                refresh()
                self.app.toast.show("Saved", f"Added to {list_name}", "ok")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def delete_val():
            sel = lb.curselection()
            if not sel:
                return
            val = lb.get(sel[0])
            if not messagebox.askyesno("Delete", f"Remove '{val}'?"):
                return
            db_execute(
                "DELETE FROM config_lists WHERE list_name=? AND list_value=?",
                (list_name, val))
            self.app.config = get_config()
            refresh()
            self.app.toast.show("Deleted", list_name, "warn")

        ttk.Button(add_f, text="Add", style="Primary.TButton",
                   command=add_val).pack(side="right")
        ttk.Button(box, text="Delete selected", style="Danger.TButton",
                   command=delete_val).pack(anchor="e", pady=(6, 0))

        refresh()
