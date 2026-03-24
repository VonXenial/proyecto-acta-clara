"""
Vista de Historial - ActaClara v1.2.1
"""
import tkinter as tk
from tkinter import ttk
from src.ui.styles import COLORS, FONTS

class HistoryView(tk.Frame):
    VIEW_NAME = "history"
    def __init__(self, parent, db_manager, on_select=None, theme="light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["bg"])
        self.db = db_manager
        self.on_select = on_select
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=self.c["bg"], pady=30, padx=40)
        header.pack(fill="x")
        tk.Label(header, text="Historial de Reuniones", bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")
        
        frame = tk.Frame(self, bg=self.c["bg"], padx=40, pady=10)
        frame.pack(fill="both", expand=True)
        
        cols = ("ID", "Título", "Fecha", "Idioma", "Estado")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.refresh_data()

    def refresh_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        if self.db:
            actas = self.db.get_all_actas()
            for a in actas:
                fecha = a.fecha_creacion.strftime("%d/%m/%Y %H:%M")
                self.tree.insert("", "end", values=(a.id, a.titulo, fecha, a.idioma, "✅ Procesada"))
