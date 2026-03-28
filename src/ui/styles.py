"""
Estilos globales de ActaClara
Paleta de colores corporativa y configuración de ttk avanzada.
"""

import tkinter as tk
from tkinter import ttk

# ── Paleta de Colores ────────────────────────────────────────
COLORS = {
    "light": {
        "primary":      "#2E75B6",
        "primary_hover":"#1F5280",
        "success":      "#28A745",
        "warning":      "#FF8C00",
        "warning_light":"#FFF3E0",
        "danger":       "#DC3545",
        "live_red":     "#DC3545",
        "bg":           "#F5F7FA",
        "card_bg":      "#FFFFFF",
        "sidebar_bg":   "#1E2A3A",
        "sidebar_text": "#A8B8CC",
        "sidebar_active":"#2E75B6",
        "sidebar_hover":"#253447",
        "text_primary": "#1A2332",
        "text_secondary":"#6B7A8D",
        "border":       "#E1E8F0",
    },
    "dark": {
        "primary":      "#4A90E2",
        "primary_hover":"#357ABD",
        "success":      "#2ECC71",
        "warning":      "#F39C12",
        "warning_light":"#78350F",
        "danger":       "#EF4444",
        "live_red":     "#EF4444",
        "bg":           "#121417",
        "card_bg":      "#1E2128",
        "sidebar_bg":   "#1A1D21",
        "sidebar_text": "#9CA3AF",
        "sidebar_active":"#4A90E2",
        "sidebar_hover":"#1A2332",
        "text_primary": "#F9FAFB",
        "text_secondary":"#9CA3AF",
        "border":       "#2D333B",
    }
}

FONTS = {}

def set_font_scale(scale: str):
    base = {"pequeño": 8, "mediano": 10, "grande": 12, "extra_grande": 14}
    sz = base.get(scale, 10)
    FONTS["title"] = ("Segoe UI", sz + 12, "bold")
    FONTS["heading"] = ("Segoe UI", sz + 4, "bold")
    FONTS["body"] = ("Segoe UI", sz)  # type: ignore
    FONTS["small"] = ("Segoe UI", sz - 1)  # type: ignore
    FONTS["mono"] = ("Consolas", sz)  # type: ignore
    FONTS["badge"] = ("Segoe UI", sz - 1, "bold")

set_font_scale("mediano")

DIMENSIONS = {
    "window_width":     1366,
    "window_height":    768,
    "sidebar_width":    220,
    "padding_large":    32,
    "padding_medium":   20,
    "padding_small":    12,
    "padding_tiny":     8,
    "border_radius":    8,
}

def apply_styles(root: tk.Tk, theme="light"):
    """Aplica estilos globales ttk avanzados."""
    c = COLORS[theme]
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── BOTONES PERSONALIZADOS ──
    style.configure("Primary.TButton", background=c["primary"], foreground="white", 
                    font=("Segoe UI", 11, "bold"), padding=(20, 10), borderwidth=0)
    style.map("Primary.TButton", background=[("active", c["primary_hover"])])

    style.configure("Success.TButton", background=c["success"], foreground="white", 
                    font=("Segoe UI", 10, "bold"), padding=(14, 8), borderwidth=0)
    style.map("Success.TButton", background=[("active", "#1E7E34")])

    style.configure("Secondary.TButton", background=c["card_bg"], foreground=c["text_primary"], 
                    font=("Segoe UI", 10), padding=(14, 8), borderwidth=1, relief="solid")
    style.map("Secondary.TButton", background=[("active", c["bg"])])

    style.configure("Danger.TButton", background=c["danger"], foreground="white", 
                    font=("Segoe UI", 11, "bold"), padding=(20, 10), borderwidth=0)

    # ── TREEVIEW (TABLAS PROFESIONALES) ──
    style.configure("Treeview", 
                    background=c["card_bg"], 
                    foreground=c["text_primary"],
                    rowheight=40,
                    fieldbackground=c["card_bg"],
                    font=FONTS["body"],
                    borderwidth=0)
    
    style.configure("Treeview.Heading", 
                    background=c["bg"], 
                    foreground=c["text_secondary"],
                    font=FONTS["small"],
                    relief="flat",
                    padding=10)
    
    style.map("Treeview", 
              background=[("selected", c["primary"])],
              foreground=[("selected", "white")])

    # ── COMBOBOX PROFESIONAL ──
    style.configure("TCombobox", 
                    font=FONTS["body"], 
                    fieldbackground=c["card_bg"], 
                    background=c["border"],
                    arrowcolor=c["primary"],
                    borderwidth=1,
                    relief="flat")
    
    style.map("TCombobox",
              fieldbackground=[("readonly", c["card_bg"])],
              foreground=[("readonly", c["text_primary"])])

    # ── ENTRY (INPUTS) PROFESIONAL ──
    style.configure("TEntry", 
                    fieldbackground=c["card_bg"], 
                    foreground=c["text_primary"],
                    padding=5)
    
    style.map("TEntry",
              fieldbackground=[("focus", c["card_bg"]), ("readonly", c["bg"])],
              foreground=[("focus", c["text_primary"])])

    style.configure("TProgressbar", troughcolor=c["border"], background=c["primary"], thickness=10)
    style.configure("Blue.Horizontal.TProgressbar", troughcolor=c["border"], background=c["primary"], thickness=8)
    
    # Checkbuttons y Radiobuttons
    style.configure("TCheckbutton", background=c["card_bg"], foreground=c["text_primary"], font=FONTS["body"])
    style.configure("TRadiobutton", background=c["card_bg"], foreground=c["text_primary"], font=FONTS["body"])

    return c
