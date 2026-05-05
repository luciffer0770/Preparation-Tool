import tkinter as tk
from tkinter import ttk

C = {
    "red":          "#ED0007",
    "red_dark":     "#B71C1C",
    "red_light":    "#FFEBEE",
    "black":        "#000000",
    "bg":           "#F0F4F8",
    "card":         "#FFFFFF",
    "border":       "#E0E4E8",
    "row_alt":      "#F5F7FA",
    "text":         "#37474F",
    "muted":        "#78909C",
    "amber":        "#E65100",
    "amber_light":  "#FFF8E1",
    "amber_row":    "#FFF3E0",
    "green":        "#1B5E20",
    "green_light":  "#E8F5E9",
    "blue":         "#0D47A1",
    "blue_mid":     "#1565C0",
    "blue_light":   "#E3F2FD",
    "purple":       "#4A148C",
    "violet_light": "#F3E5F5",
    "steel":        "#37474F",
    "steel_light":  "#ECEFF1",
    "white":        "#FFFFFF",
    "accent_bg":    "#E8EAF6",
}

STATUS_BG = {
    "Not Started": C["row_alt"],
    "In Progress":  C["blue_light"],
    "Complete":     C["green_light"],
    "Blocked":      C["red_light"],
    "Delayed":      C["amber_row"],
    "On Hold":      C["violet_light"],
}
STATUS_FG = {
    "Not Started": C["text"],
    "In Progress":  C["blue"],
    "Complete":     C["green"],
    "Blocked":      C["red_dark"],
    "Delayed":      C["amber"],
    "On Hold":      C["purple"],
}

import sys
if sys.platform == "win32":
    F_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    F_FAMILY = "SF Pro Display"
else:
    F_FAMILY = "DejaVu Sans"

F = {
    "h1":      (F_FAMILY, 18, "bold"),
    "h2":      (F_FAMILY, 13, "bold"),
    "h3":      (F_FAMILY, 11, "bold"),
    "body":    (F_FAMILY, 10),
    "body_b":  (F_FAMILY, 10, "bold"),
    "small":   (F_FAMILY, 9),
    "small_b": (F_FAMILY, 9, "bold"),
    "caption": (F_FAMILY, 8),
    "mono":    ("Consolas" if sys.platform == "win32" else "Courier New", 10),
    "kpi":     (F_FAMILY, 28, "bold"),
    "kpi_sm":  (F_FAMILY, 20, "bold"),
}


def apply_theme():
    """Configure ttk styles. Use integer padding only (tuple padding breaks some Tk builds)."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".",
        background=C["bg"],
        foreground=C["text"],
        font=F["body"],
        relief="flat",
        borderwidth=0,
    )

    style.configure("TFrame",      background=C["bg"])
    style.configure("Card.TFrame", background=C["card"])
    style.configure("Side.TFrame", background=C["steel"])
    style.configure("Bar.TFrame",  background=C["card"])
    style.configure("Header.TFrame", background=C["card"])

    style.configure("TLabel",        background=C["bg"],    foreground=C["text"],  font=F["body"])
    style.configure("Card.TLabel",   background=C["card"],  foreground=C["text"],  font=F["body"])
    style.configure("H1.TLabel",     background=C["card"],  foreground="#111111",  font=F["h1"])
    style.configure("H2.TLabel",     background=C["card"],  foreground="#111111",  font=F["h2"])
    style.configure("H3.TLabel",     background=C["card"],  foreground="#111111",  font=F["h3"])
    style.configure("Muted.TLabel",  background=C["bg"],    foreground=C["muted"], font=F["small"])
    style.configure("Caption.TLabel",background=C["bg"],    foreground=C["muted"], font=F["caption"])
    style.configure("Red.TLabel",    background=C["card"],  foreground=C["red"],   font=F["body_b"])
    style.configure("Mono.TLabel",   background=C["card"],  foreground=C["blue"],  font=F["mono"])
    style.configure("KPI.TLabel",    background=C["card"],  foreground="#000000",  font=F["kpi"])
    style.configure("KPI_S.TLabel",  background=C["card"],  foreground="#000000",  font=F["kpi_sm"])

    style.configure("Primary.TButton",
        background=C["red"], foreground="white",
        font=F["small_b"], padding=10,
        borderwidth=0, relief="flat")
    style.map("Primary.TButton",
        background=[("active", "#C50006"), ("pressed", "#A00005")],
        foreground=[("active", "white")])

    style.configure("Secondary.TButton",
        background=C["card"], foreground="#111111",
        font=F["small_b"], padding=10,
        borderwidth=1, relief="solid")
    style.map("Secondary.TButton",
        background=[("active", C["row_alt"]), ("pressed", C["border"])])

    style.configure("Ghost.TButton",
        background=C["bg"], foreground=C["text"],
        font=F["small"], padding=6,
        borderwidth=0, relief="flat")
    style.map("Ghost.TButton",
        background=[("active", C["row_alt"])])

    style.configure("Danger.TButton",
        background=C["card"], foreground=C["red_dark"],
        font=F["small_b"], padding=10,
        borderwidth=1, relief="solid")
    style.map("Danger.TButton",
        background=[("active", C["red_light"])])

    style.configure("NavActive.TButton",
        background=C["steel"], foreground="white",
        font=F["body_b"], padding=10,
        borderwidth=0, relief="flat", anchor="w")

    style.configure("NavItem.TButton",
        background=C["steel"], foreground=C["steel_light"],
        font=F["body"], padding=10,
        borderwidth=0, relief="flat", anchor="w")
    style.map("NavItem.TButton",
        background=[("active", "#455A64")])

    style.configure("Treeview",
        background=C["card"],
        foreground=C["text"],
        rowheight=28,
        fieldbackground=C["card"],
        font=F["body"],
        borderwidth=0,
        relief="flat")
    style.configure("Treeview.Heading",
        background=C["steel_light"],
        foreground=C["steel"],
        font=F["small_b"],
        relief="flat",
        borderwidth=1,
        padding=8)
    style.map("Treeview",
        background=[("selected", C["blue_light"])],
        foreground=[("selected", C["blue"])])
    style.map("Treeview.Heading",
        background=[("active", C["border"])])

    style.configure("TEntry",
        fieldbackground=C["card"],
        foreground="#111111",
        font=F["body"],
        padding=6,
        borderwidth=1,
        relief="solid")
    style.map("TEntry",
        bordercolor=[("focus", C["red"])])

    style.configure("TCombobox",
        fieldbackground=C["card"],
        foreground="#111111",
        font=F["body"],
        padding=6)

    style.configure("TSpinbox",
        fieldbackground=C["card"],
        foreground="#111111",
        font=F["body"],
        padding=6)

    style.configure("TScrollbar",
        background=C["bg"],
        troughcolor=C["row_alt"],
        borderwidth=0,
        arrowsize=11)
    style.map("TScrollbar",
        background=[("active", "#B0BEC5"), ("!active", "#CFD8DC")])

    style.configure("TSeparator", background=C["border"])
