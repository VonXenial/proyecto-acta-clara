"""
Sidebar de navegación con items clickeables y soporte de temas.
"""

import os
import tkinter as tk
from tkinter import ttk
from src.ui.styles import COLORS, FONTS # type: ignore
from typing import Dict, Any, Tuple, Optional
from src.utils.i18n import translate as _  # type: ignore

# Definición de items de navegación (Normalizados para evitar glitches de espacio)
NAV_ITEMS = [
    ("dashboard",     "📊", "Dashboard"),
    ("transcription", "🎙️", "Transcripción"),
    ("history",       "📅", "Historial"),
    ("export",        "📤", "Exportación"),
    ("config",        "⚙️", "Configuración"),
]

class Sidebar(tk.Frame):
    """Barra lateral de navegación."""
    
    def __init__(self, parent, on_navigate, theme="light", lang="Español"):
        """
        Inicializa el sidebar con soporte de tema.
        """
        self.c = COLORS[theme]
        self.lang = lang
        super().__init__(
            parent,
            bg=self.c["sidebar_bg"],
            width=220,
        )
        
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self._buttons = {}
        self.current_active = "dashboard"
        self.logo_img: Optional[tk.PhotoImage] = None
        
        self._build_header()
        self._build_navigation()
        self._build_footer()
    
    def _build_header(self):
        header = tk.Frame(self, bg=self.c["sidebar_bg"], pady=12)
        header.pack(fill="x")
        
        try:
            from src.config import APP_DIR  # type: ignore
            source_path = os.path.join(APP_DIR, "assets", "logo", "logo_monochrome.png")
            if os.path.exists(source_path):
                self.logo_img = tk.PhotoImage(file=source_path)
                
                # Ajuste de tamaño (subsample para hacerlo caber mejor)
                self.logo_img = self.logo_img.subsample(3, 3) # type: ignore
                
                logo_label = tk.Label(header, image=self.logo_img, bg=self.c["sidebar_bg"]) # type: ignore
                logo_label.pack(pady=(12, 4))
        except Exception:
            pass

        tk.Label(header, text=_("ActaClara", self.lang), bg=self.c["sidebar_bg"], fg="white", 
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(header, text=_("Transcripción inteligente", self.lang), bg=self.c["sidebar_bg"], 
                 fg=self.c["sidebar_text"], font=FONTS["small"]).pack(pady=(0, 12))
        
        tk.Frame(self, bg=self.c["primary"], height=2).pack(fill="x", padx=16)

    def _build_navigation(self):
        nav_frame = tk.Frame(self, bg=self.c["sidebar_bg"])
        nav_frame.pack(fill="x", pady=16)
        
        for key, icon, label in NAV_ITEMS:
            btn = NavButton(
                nav_frame,
                icon=icon,
                label=_(label, self.lang),
                command=lambda k=key: self.on_navigate(k),
                palette=self.c
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._buttons[key] = btn
    
    def _build_footer(self):
        tk.Label(self, text="v1.4.0 Pro", bg=self.c["sidebar_bg"], 
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
        
        # Reduje ligeramente el padx exterior para equilibrar el espacio
        self.inner = tk.Frame(self, bg=self.c["sidebar_bg"], pady=10, padx=16)
        self.inner.pack(side="left", fill="both", expand=True)
        
        # 1. Contenedor de ancho y alto fijos (ampliado a 32px para emojis anchos)
        self.icon_container = tk.Frame(self.inner, bg=self.c["sidebar_bg"], width=32, height=32)
        self.icon_container.pack(side="left")
        self.icon_container.pack_propagate(False) 
        
        # 2. Centrado absoluto perfecto
        self.icon_lbl = tk.Label(self.icon_container, text=icon.strip(), bg=self.c["sidebar_bg"], 
                                 fg=self.c["sidebar_text"], font=("Segoe UI Emoji", 12))
        self.icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # 3. Reducir el padx aquí acerca el texto al icono
        self.lbl = tk.Label(self.inner, text=label, bg=self.c["sidebar_bg"], 
                            fg=self.c["sidebar_text"], font=FONTS["body"], anchor="w")
        self.lbl.pack(side="left", fill="x", expand=True, padx=(6, 0))
        
        for widget in (self, self.inner, self.lbl, self.icon_lbl, self.icon_container):
            widget.bind("<Button-1>", lambda e: command()) # type: ignore
            widget.bind("<Enter>", self._on_enter) # type: ignore
            widget.bind("<Leave>", self._on_leave) # type: ignore
    
    def set_active(self, active: bool):
        self._active = active
        bg_color = self.c["sidebar_active"] if active else self.c["sidebar_bg"]
        fg_color = "white" if active else self.c["sidebar_text"]
        self.indicator.configure(bg=self.c["primary"] if active else self.c["sidebar_bg"])
        self.configure(bg=bg_color)
        self.inner.configure(bg=bg_color)
        self.icon_container.configure(bg=bg_color)
        self.lbl.configure(bg=bg_color, fg=fg_color)
        self.icon_lbl.configure(bg=bg_color, fg=fg_color)
    
    def _on_enter(self, event=None):
        if not self._active:
            self.configure(bg=self.c["sidebar_hover"])
            self.inner.configure(bg=self.c["sidebar_hover"])
            self.icon_container.configure(bg=self.c["sidebar_hover"])
            self.lbl.configure(bg=self.c["sidebar_hover"])
            self.icon_lbl.configure(bg=self.c["sidebar_hover"])
    
    def _on_leave(self, event=None):
        if not self._active:
            self.configure(bg=self.c["sidebar_bg"])
            self.inner.configure(bg=self.c["sidebar_bg"])
            self.icon_container.configure(bg=self.c["sidebar_bg"])
            self.lbl.configure(bg=self.c["sidebar_bg"])
            self.icon_lbl.configure(bg=self.c["sidebar_bg"])
