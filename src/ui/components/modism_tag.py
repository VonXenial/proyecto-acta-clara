"""
Tooltip interactivo para modismos con botones de acción
"""

import tkinter as tk
from tkinter import ttk
from src.ui.styles import COLORS # type: ignore

class ModismTooltip(tk.Toplevel):
    """
    Tooltip interactivo que aparece sobre modismos detectados.
    Incluye botones: Aceptar, Editar, Ignorar
    """
    
    def __init__(self, parent, modismo_original: str, sugerencia: str, 
                 position: tuple, on_action=None, theme: str = "light"):
        super().__init__(parent)
        
        self.c = COLORS[theme]
        self.modismo_original = modismo_original
        self.sugerencia = sugerencia
        self.on_action = on_action
        
        self.wm_overrideredirect(True)
        self.wm_geometry(f"+{position[0]}+{position[1]}")
        self.configure(bg=self.c["text_primary"])
        
        self._build_content()
    
    def _build_content(self):
        c = self.c

        frame = tk.Frame(self, bg=c["text_primary"], padx=12, pady=10)
        frame.pack()
        
        tk.Label(frame, text=f'Original: "{self.modismo_original}"', 
                 bg=c["text_primary"], fg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        tk.Label(frame, text=f'→ "{self.sugerencia}"', 
                 bg=c["text_primary"], fg="#A8B8CC", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 10))
        
        btn_frame = tk.Frame(frame, bg=c["text_primary"])
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="✓ Aceptar", style="Success.TButton", 
                   command=lambda: self._handle_action("accept"), width=10).pack(side="left", padx=2)
        
        ttk.Button(btn_frame, text="✎ Editar", style="Secondary.TButton", 
                   command=lambda: self._handle_action("edit"), width=10).pack(side="left", padx=2)
        
        ttk.Button(btn_frame, text="✕ Ignorar", style="Secondary.TButton", 
                   command=lambda: self._handle_action("ignore"), width=10).pack(side="left", padx=2)
    
    def _handle_action(self, action: str):
        if self.on_action:
            self.on_action(action, self.modismo_original, self.sugerencia)
        self.destroy()
