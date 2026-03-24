"""
Sidebar de navegación con items clickeables y soporte de temas.
"""

import tkinter as tk
from src.ui.styles import COLORS, FONTS

# Definición de items de navegación
NAV_ITEMS = [
    ("dashboard",     "📊", "Dashboard"),
    ("transcription", "🎙️", "Transcripción"),
    ("history",       "📅", "Historial"),
    ("export",        "📤", "Exportación"),
    ("config",        "⚙️", "Configuración"),
]

class Sidebar(tk.Frame):
    """Barra lateral de navegación."""
    
    def __init__(self, parent, on_navigate, theme="light"):
        """
        Inicializa el sidebar con soporte de tema.
        """
        self.c = COLORS[theme]
        super().__init__(
            parent,
            bg=self.c["sidebar_bg"],
            width=220,
        )
        
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self._buttons = {}
        
        self._build_header()
        self._build_navigation()
        self._build_footer()
    
    def _build_header(self):
        header = tk.Frame(self, bg=self.c["sidebar_bg"], pady=24)
        header.pack(fill="x")
        
        tk.Label(header, text="ActaClara", bg=self.c["sidebar_bg"], fg="white", 
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(header, text="Transcripción inteligente", bg=self.c["sidebar_bg"], 
                 fg=self.c["sidebar_text"], font=FONTS["small"]).pack()
        
        tk.Frame(self, bg=self.c["primary"], height=2).pack(fill="x", padx=16)
    
    def _build_navigation(self):
        nav_frame = tk.Frame(self, bg=self.c["sidebar_bg"])
        nav_frame.pack(fill="x", pady=16)
        
        for key, icon, label in NAV_ITEMS:
            btn = NavButton(
                nav_frame,
                icon=icon,
                label=label,
                command=lambda k=key: self.on_navigate(k),
                palette=self.c
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._buttons[key] = btn
    
    def _build_footer(self):
        tk.Label(self, text="v1.2.0 Pro", bg=self.c["sidebar_bg"], 
                 fg=self.c["sidebar_text"], font=FONTS["small"]).pack(side="bottom", pady=16)
    
    def set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)

class NavButton(tk.Frame):
    """Botón de navegación del sidebar con estado activo."""
    def __init__(self, parent, icon, label, command, palette):
        super().__init__(parent, bg=palette["sidebar_bg"], cursor="hand2")
        self.command = command
        self.c = palette
        self._active = False
        
        self.indicator = tk.Frame(self, width=4, bg=self.c["sidebar_bg"])
        self.indicator.pack(side="left", fill="y")
        
        self.inner = tk.Frame(self, bg=self.c["sidebar_bg"], pady=10, padx=12)
        self.inner.pack(side="left", fill="both", expand=True)
        
        self.lbl = tk.Label(self.inner, text=f"{icon}  {label}", bg=self.c["sidebar_bg"], 
                            fg=self.c["sidebar_text"], font=FONTS["body"], anchor="w")
        self.lbl.pack(fill="x")
        
        for widget in (self, self.inner, self.lbl):
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def set_active(self, active: bool):
        self._active = active
        bg_color = self.c["sidebar_active"] if active else self.c["sidebar_bg"]
        fg_color = "white" if active else self.c["sidebar_text"]
        self.indicator.configure(bg=self.c["primary"] if active else self.c["sidebar_bg"])
        self.configure(bg=bg_color)
        self.inner.configure(bg=bg_color)
        self.lbl.configure(bg=bg_color, fg=fg_color)
    
    def _on_enter(self, event=None):
        if not self._active:
            self.configure(bg=self.c["sidebar_hover"])
            self.inner.configure(bg=self.c["sidebar_hover"])
            self.lbl.configure(bg=self.c["sidebar_hover"])
    
    def _on_leave(self, event=None):
        if not self._active:
            self.configure(bg=self.c["sidebar_bg"])
            self.inner.configure(bg=self.c["sidebar_bg"])
            self.lbl.configure(bg=self.c["sidebar_bg"])
