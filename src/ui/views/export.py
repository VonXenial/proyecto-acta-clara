"""
Vista Exportación - ActaClara v1.2.1
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.styles import COLORS, FONTS, DIMENSIONS

class ExportView(tk.Frame):
    VIEW_NAME = "export"
    def __init__(self, parent, theme="light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["bg"])
        self._titulo_var = tk.StringVar(value="Reunión de Planificación")
        self._objetivo_var = tk.StringVar(value="Definir hitos y cronograma")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=self.c["bg"], pady=20, padx=40)
        header.pack(fill="x")
        tk.Label(header, text="Estructura del Acta", bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")
        
        body = tk.Frame(self, bg=self.c["bg"], padx=40)
        body.pack(fill="both", expand=True)
        
        card = tk.Frame(body, bg=self.c["card_bg"], padx=30, pady=30,
                        highlightbackground=self.c["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)
        
        tk.Label(card, text="Título de la reunión", bg=self.c["card_bg"], fg=self.c["text_secondary"]).pack(anchor="w")
        ttk.Entry(card, textvariable=self._titulo_var).pack(fill="x", pady=10)
        
        tk.Label(card, text="Objetivo", bg=self.c["card_bg"], fg=self.c["text_secondary"]).pack(anchor="w")
        ttk.Entry(card, textvariable=self._objetivo_var).pack(fill="x", pady=10)
        
        ttk.Button(card, text="📥 Generar Documento", style="Primary.TButton", 
                   command=lambda: messagebox.showinfo("Exportar", "Generando acta...")).pack(pady=20)
