import os
import sys
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.theme import C, F
from backend.database import db_execute, db_fetchone


DOC_ICON = {
    "PDF": "📄",
    "Word": "📊",
    "Excel": "📊",
    "Drawing": "📐",
    "Web": "🌐",
    "Other": "📁",
}


class DocumentsModule:
    COLS = ("Type", "Title", "Category", "Rev", "Added", "By", "Status", "Path", "Open")

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

    def render(self):
        docs = self.app.documents
        total = len(docs)
        n_word = sum(1 for d in docs if d.get("doc_type") == "Word")
        n_excel = sum(1 for d in docs if d.get("doc_type") == "Excel")
        n_pdf = sum(1 for d in docs if d.get("doc_type") == "PDF")
        n_draw = sum(1 for d in docs if d.get("doc_type") == "Drawing")
        n_web = sum(1 for d in docs if d.get("doc_type") == "Web")

        sum_row = tk.Frame(self.parent, bg=C["row_alt"], padx=12, pady=8)
        sum_row.pack(fill="x", pady=(0, 8))
        txt = (f"Total: {total}   |   Word: {n_word}   Excel: {n_excel}   "
               f"PDF: {n_pdf}   Drawing: {n_draw}   Web: {n_web}")
        tk.Label(sum_row, text=txt, font=F["small"], bg=C["row_alt"], fg=C["text"]).pack(anchor="w")

        toolbar = tk.Frame(self.parent, bg=C["card"], padx=12, pady=8)
        toolbar.pack(fill="x", pady=(0, 8))
        toolbar.configure(highlightbackground=C["border"], highlightthickness=1)
        ttk.Button(toolbar, text="+ Add Document", style="Primary.TButton",
                   command=self._add_doc).pack(side="right")
        ttk.Button(toolbar, text="⟳ Refresh", style="Ghost.TButton",
                   command=lambda: self.app.refresh()).pack(side="left")

        tbl_frame = tk.Frame(self.parent, bg=C["card"])
        tbl_frame.pack(fill="both", expand=True)
        tbl_frame.configure(highlightbackground=C["border"], highlightthickness=1)

        self.tree = ttk.Treeview(tbl_frame, columns=self.COLS, show="headings")
        widths = (50, 200, 140, 50, 85, 80, 100, 220, 70)
        for c, w in zip(self.COLS, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)

        self.tree.tag_configure("doc_active", background=C["green_light"])
        self.tree.tag_configure("doc_review", background=C["amber_light"])
        self.tree.tag_configure("doc_other", background=C["card"])

        vsb = ttk.Scrollbar(tbl_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for d in docs:
            dt = d.get("doc_type") or "Other"
            icon = DOC_ICON.get(dt, DOC_ICON["Other"])
            dst = d.get("doc_status") or "Active"
            if dst == "Active":
                dtag = "doc_active"
            elif dst == "Under Review":
                dtag = "doc_review"
            else:
                dtag = "doc_other"
            self.tree.insert("", "end", iid=str(d["id"]), tags=(dtag,), values=(
                f"{icon} {dt}",
                d.get("title", ""),
                d.get("category", ""),
                d.get("revision", ""),
                d.get("date_added", ""),
                d.get("added_by", ""),
                dst,
                (d.get("file_path") or "")[:50],
                "Open",
            ))

        self.tree.bind("<Double-1>", self._on_double)

    def _open_path(self, path: str):
        path = (path or "").strip()
        if not path:
            messagebox.showwarning("Open", "No path set.")
            return
        low = path.lower()
        if low.startswith("http://") or low.startswith("https://"):
            webbrowser.open(path)
            return
        if not os.path.isfile(path):
            messagebox.showerror("Open", f"File not found:\n{path}")
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Open", str(e))

    def _on_double(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row:
            return
        if col != "#9":
            return
        doc = db_fetchone("SELECT * FROM documents WHERE id=?", (int(row),))
        if doc:
            self._open_path(doc.get("file_path") or "")

    def _add_doc(self):
        path = filedialog.askopenfilename(title="Select document file")
        if not path:
            return

        cfg = self.app.config
        dlg = tk.Toplevel(self.app.root)
        dlg.title("New Document")
        dlg.geometry("420x380")
        dlg.grab_set()
        dlg.configure(bg=C["card"])

        vars_map = {}
        fields = [
            ("Title *", "title", "entry", None),
            ("Doc Type", "doc_type", "combo", cfg.get("doc_type", [])),
            ("Category", "category", "combo", cfg.get("doc_category", [])),
            ("Revision", "revision", "entry", None),
            ("Added By", "added_by", "entry", None),
            ("Status", "doc_status", "combo", cfg.get("doc_status", [])),
        ]
        body = tk.Frame(dlg, bg=C["card"], padx=16, pady=12)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=f"File:\n{path}", font=F["small"], bg=C["card"],
                 fg=C["muted"], wraplength=380, justify="left").pack(anchor="w", pady=(0, 8))

        for label, key, kind, opts in fields:
            tk.Label(body, text=label.upper(), font=F["caption"],
                     bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(6, 0))
            var = tk.StringVar()
            vars_map[key] = var
            if kind == "combo":
                ttk.Combobox(body, textvariable=var, values=opts or [], state="readonly").pack(fill="x")
            else:
                ttk.Entry(body, textvariable=var).pack(fill="x")

        vars_map["title"].set(os.path.basename(path))

        foot = tk.Frame(dlg, bg=C["card"], padx=16, pady=12)
        foot.pack(fill="x")

        def save():
            title = vars_map["title"].get().strip()
            if not title:
                messagebox.showwarning("Required", "Title is required.")
                return
            db_execute("""INSERT INTO documents
                (project_id, doc_type, title, category, revision, added_by, doc_status, file_path)
                VALUES (?,?,?,?,?,?,?,?)""",
                (self.app.active_project_id,
                 vars_map["doc_type"].get() or "PDF",
                 title,
                 vars_map["category"].get() or "",
                 vars_map["revision"].get() or "—",
                 vars_map["added_by"].get() or "",
                 vars_map["doc_status"].get() or "Active",
                 path))
            dlg.destroy()
            self.app.refresh()
            self.app.toast.show("Saved", "Document added", "ok")

        ttk.Button(foot, text="Save", style="Primary.TButton", command=save).pack(side="right")
