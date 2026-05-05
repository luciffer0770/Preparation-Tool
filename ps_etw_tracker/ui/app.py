import sys
import tkinter as tk
from tkinter import ttk
from ui.theme import apply_theme, C, F
from ui.widgets.topbar import TopBar
from ui.widgets.sidebar import Sidebar
from ui.widgets.toast import ToastManager
from backend.database import (
    get_projects,
    get_activities,
    get_materials,
    get_delays,
    get_documents,
    get_config,
    recompute_material_alerts,
)


class PSETWApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PS-ETW Engine Build-Up Tracker — Bosch RBIN PS-ETW1")
        self.root.minsize(1280, 768)
        self.root.geometry("1440x900")
        self.root.configure(bg=C["bg"])

        apply_theme()

        self.active_project_id: str | None = None
        self.active_tab: str = "dashboard"
        self.projects: list[dict] = []
        self.activities: list[dict] = []
        self.materials: list[dict] = []
        self.delays: list[dict] = []
        self.documents: list[dict] = []
        self.config: dict = {}
        self.sidebar_collapsed: bool = False

        self._module_cache: dict = {}

        self.toast = ToastManager(self.root)

        self._build_shell()
        self._load_all()

    def _build_shell(self):
        self.topbar = TopBar(self.root, app=self)
        self.topbar.frame.pack(side="top", fill="x")

        self.body = tk.Frame(self.root, bg=C["bg"])
        self.body.pack(side="top", fill="both", expand=True)

        self.sidebar = Sidebar(self.body, app=self)
        self.sidebar.frame.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self.body, bg=C["bg"])
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.content_frame = tk.Frame(self.main_frame, bg=C["bg"])
        self.content_frame.pack(side="top", fill="both", expand=True)

    def _load_all(self):
        self.config = get_config()
        self.projects = get_projects()
        active = next((p for p in self.projects if not p.get("archived")), None)
        if active:
            self.active_project_id = active["id"]
            self._load_project_data()
        else:
            self.active_project_id = None
        self.topbar.update()
        self.sidebar.update()
        self.render_module()

    def _load_project_data(self):
        if not self.active_project_id:
            return
        recompute_material_alerts(self.active_project_id)
        self.activities = get_activities(self.active_project_id)
        self.materials = get_materials(self.active_project_id)
        self.delays = get_delays(self.active_project_id)
        self.documents = get_documents(self.active_project_id)

    def refresh(self):
        self.config = get_config()
        self.projects = get_projects()
        if self.active_project_id:
            cur = next((p for p in self.projects if p["id"] == self.active_project_id), None)
            if not cur or cur.get("archived"):
                self.active_project_id = next(
                    (p["id"] for p in self.projects if not p.get("archived")), None)
        self._load_project_data()
        self.topbar.update()
        self.sidebar.update()
        self.render_module()

    def select_project(self, project_id: str):
        self.active_project_id = project_id
        self.active_tab = "dashboard"
        self._module_cache.clear()
        self._load_project_data()
        self.topbar.update()
        self.sidebar.update()
        self.render_module()

    def navigate(self, tab: str):
        self.active_tab = tab
        self.sidebar.update()
        self.render_module()

    def render_module(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.content_frame, bg=C["bg"], highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["bg"])
        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_canvas_resize(e):
            canvas.itemconfig(canvas_window, width=e.width)
        canvas.bind("<Configure>", on_canvas_resize)

        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def _on_mousewheel_linux_up(e):
            canvas.yview_scroll(-1, "units")

        def _on_mousewheel_linux_down(e):
            canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        if sys.platform.startswith("linux"):
            canvas.bind_all("<Button-4>", _on_mousewheel_linux_up)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux_down)

        pad = tk.Frame(inner, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=16, pady=12)

        if not self.active_project_id and self.active_tab not in ("all_projects", "settings"):
            self._render_welcome(pad)
            return

        tab = self.active_tab
        if tab == "dashboard":
            from ui.modules.dashboard import DashboardModule
            DashboardModule(pad, self).render()
        elif tab == "activities":
            from ui.modules.activities import ActivitiesModule
            ActivitiesModule(pad, self).render()
        elif tab == "gantt":
            from ui.modules.gantt import GanttModule
            GanttModule(pad, self).render()
        elif tab == "calendar":
            from ui.modules.calendar_view import CalendarModule
            if "calendar" not in self._module_cache:
                self._module_cache["calendar"] = CalendarModule(pad, self)
            else:
                self._module_cache["calendar"].parent = pad
                self._module_cache["calendar"].app = self
            self._module_cache["calendar"].render()
        elif tab == "materials":
            from ui.modules.materials import MaterialsModule
            MaterialsModule(pad, self).render()
        elif tab == "delays":
            from ui.modules.delays import DelaysModule
            DelaysModule(pad, self).render()
        elif tab == "documents":
            from ui.modules.documents import DocumentsModule
            DocumentsModule(pad, self).render()
        elif tab == "reports":
            from ui.modules.reports import ReportsModule
            ReportsModule(pad, self).render()
        elif tab == "settings":
            from ui.modules.settings import SettingsModule
            SettingsModule(pad, self).render()
        elif tab == "all_projects":
            from ui.modules.all_projects import AllProjectsModule
            AllProjectsModule(pad, self).render()

    def _render_welcome(self, parent: tk.Frame):
        card = tk.Frame(parent, bg=C["card"], padx=40, pady=40)
        card.pack(fill="both", expand=True)
        card.configure(highlightbackground=C["border"], highlightthickness=1)
        tk.Label(card, text="PS-ETW Engine Build-Up Tracker",
                 font=F["h1"], bg=C["card"], fg="#111111").pack(anchor="w")
        tk.Label(card, text="No project selected. Create a project to load the 91-activity template.",
                 font=F["body"], bg=C["card"], fg=C["muted"], wraplength=560, justify="left").pack(
            anchor="w", pady=(12, 24))
        ttk.Button(card, text="+ New Project", style="Primary.TButton",
                   command=lambda: self._open_new_project()).pack(anchor="w")

    def _open_new_project(self):
        from ui.modules.project_switcher import NewProjectDialog
        NewProjectDialog(self)
