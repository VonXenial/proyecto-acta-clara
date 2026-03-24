"""
Vista Dashboard - Pantalla principal consolidada.
Muestra estadísticas y las últimas actas procesadas directamente.
"""

import tkinter as tk
from tkinter import ttk
from src.ui.styles import COLORS, FONTS, DIMENSIONS

class DashboardView(tk.Frame):
    VIEW_NAME = "dashboard"
    
    def __init__(self, parent, on_new_session=None, db_manager=None, theme="light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["bg"])
        self.on_new_session = on_new_session
        self.db = db_manager
        self.theme = theme
        self._build()
    
    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=self.c["bg"], pady=30, padx=40)
        header.pack(fill="x")
        
        tk.Label(header, text="Panel de Control", bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")
        
        ttk.Button(header, text="+ Nueva Acta", style="Primary.TButton", 
                   command=self.on_new_session).pack(side="right")

        # ── Tarjetas KPI ───────────────────────────────────────
        kpi_frame = tk.Frame(self, bg=self.c["bg"], padx=40)
        kpi_frame.pack(fill="x")
        for i in range(4): kpi_frame.columnconfigure(i, weight=1, uniform="kpi")

        kpis = [
            ("12", "Actas Totales", self.c["primary"]),
            ("95%", "Precisión IA", self.c["success"]),
            ("8.5h", "Tiempo Total", self.c["primary"]),
            ("47", "Modismos", self.c["warning"]),
        ]
        for col, (val, lbl, clr) in enumerate(kpis):
            self._kpi_card(kpi_frame, val, lbl, clr).grid(row=0, column=col, padx=(0, 15) if col < 3 else 0, sticky="ew")

        # ── Tabla de Actas Recientes ───────────────────────────
        table_frame = tk.Frame(self, bg=self.c["bg"], padx=40, pady=30)
        table_frame.pack(fill="both", expand=True)

        tk.Label(table_frame, text="Últimas Actas Procesadas", bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["heading"]).pack(anchor="w", pady=(0, 15))

        # El Treeview ya tiene el estilo profesional definido en apply_styles
        self.tree = ttk.Treeview(table_frame, columns=("Nombre", "Fecha", "Modismos", "Estado"), 
                                 show="headings", height=8)
        
        headers = ["Nombre", "Fecha", "Modismos", "Estado"]
        for h in headers:
            self.tree.heading(h, text=h.upper())
            self.tree.column(h, width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.refresh_data()

    def _kpi_card(self, parent, value, label, color):
        card = tk.Frame(parent, bg=self.c["card_bg"], padx=20, pady=20,
                        highlightbackground=self.c["border"], highlightthickness=1)
        accent = tk.Frame(card, bg=color, width=4)
        accent.place(relheight=1, x=0, y=0)
        tk.Label(card, text=value, bg=self.c["card_bg"], fg=color, font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=10)
        tk.Label(card, text=label, bg=self.c["card_bg"], fg=self.c["text_secondary"], font=FONTS["small"]).pack(anchor="w", padx=10)
        return card

    def refresh_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        if self.db:
            actas = self.db.get_all_actas()[:5] # Solo las últimas 5
            for a in actas:
                fecha = a.fecha_creacion.strftime("%d/%m/%Y")
                modismos = len(a.modismos_detectados) if a.modismos_detectados else 0
                self.tree.insert("", "end", values=(a.titulo, fecha, modismos, "✅ Terminada"))
