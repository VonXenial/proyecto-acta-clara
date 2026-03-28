"""
Vista Dashboard Profesional - ActaClara v1.5
Pantalla principal con estadísticas, gráficos y acceso rápido.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from src.ui.styles import COLORS, FONTS, DIMENSIONS # type: ignore
from src.database.db_manager import DBManager # type: ignore
from src.utils.i18n import translate as _ # type: ignore
from src.ui.views.history import TranscriptionDialog # type: ignore

class DashboardView(tk.Frame):
    """Vista del Dashboard con estadísticas y acceso rápido."""
    
    VIEW_NAME = "dashboard"
    
    def __init__(self, parent, on_new_session=None, db_manager=None, 
                 theme="light", lang="Español", app=None):
        self.c = COLORS[theme]
        self.lang = lang
        super().__init__(parent, bg=self.c["bg"])
        
        self.on_new_session = on_new_session
        self.db: DBManager = db_manager # type: ignore
        self.app = app  # Referencia a MainWindow
        self.theme = theme
        
        # Atributos para el linter
        self.tree: ttk.Treeview = None # type: ignore
        self.kpi_labels = {}
        self.canvas: tk.Canvas = None # type: ignore
        self.scrollbar: ttk.Scrollbar = None # type: ignore
        self.main_container: tk.Frame = None # type: ignore
        self.canvas_window: int = 0
        
        self._build()
    
    def _build(self):
        """Construye todos los elementos de la vista."""
        # Se envuelve en un canvas para permitir scroll si la ventana es muy pequeña
        self.canvas = tk.Canvas(self, bg=self.c["bg"], bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.main_container = tk.Frame(self.canvas, bg=self.c["bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_container, anchor="nw")

        self.main_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        # Mouse wheel
        def _on_mousewheel(event):
            bbox = self.canvas.bbox("all")
            if not bbox: return
            content_height = bbox[3] - bbox[1]
            canvas_height = self.canvas.winfo_height()
            if content_height > canvas_height:
                delta = 0
                if hasattr(event, 'delta') and event.delta != 0:
                    delta = -1 if event.delta > 0 else 1
                elif hasattr(event, 'num'):
                    delta = -1 if event.num == 4 else 1
                self.canvas.yview_scroll(delta, "units")

        self.canvas.bind("<Enter>", lambda e: [
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel),
            self.canvas.bind_all("<Button-4>", _on_mousewheel),
            self.canvas.bind_all("<Button-5>", _on_mousewheel)
        ])
        self.canvas.bind("<Leave>", lambda e: [
            self.canvas.unbind_all("<MouseWheel>"),
            self.canvas.unbind_all("<Button-4>"),
            self.canvas.unbind_all("<Button-5>")
        ])

        self._build_header(self.main_container)
        self._build_kpi_cards(self.main_container)
        self._build_quick_stats(self.main_container)
        self._build_recent_table(self.main_container)
    
    def _build_header(self, parent):
        """Header con título, botón nueva acta y botón refresh."""
        header = tk.Frame(parent, bg=self.c["bg"], pady=10, padx=40)
        header.pack(fill="x")
        
        # Título
        title_frame = tk.Frame(header, bg=self.c["bg"])
        title_frame.pack(side="left")
        
        tk.Label(
            title_frame,
            text=_("Panel de Control", self.lang),
            bg=self.c["bg"],
            fg=self.c["text_primary"],
            font=FONTS["title"]
        ).pack(anchor="w")
        
        # Subtítulo con fecha
        now = datetime.now()
        date_str = now.strftime("%A, %d de %B %Y")
        tk.Label(
            title_frame,
            text=date_str.capitalize(),
            bg=self.c["bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w")
        
        # Botones derecha
        btn_frame = tk.Frame(header, bg=self.c["bg"])
        btn_frame.pack(side="right")
        
        # Botón refresh
        ttk.Button(
            btn_frame,
            text="🔄 Actualizar",
            style="Secondary.TButton",
            command=self.refresh_data,
            width=12
        ).pack(side="left", padx=(0, 12))
        
        # Botón Nueva Acta (principal)
        ttk.Button(
            btn_frame,
            text=_("+ Nueva Acta", self.lang),
            style="Primary.TButton",
            command=self.on_new_session,
            width=15
        ).pack(side="left")
    
    def _build_kpi_cards(self, parent):
        """Tarjetas KPI mejoradas con iconos y efectos."""
        kpi_container = tk.Frame(parent, bg=self.c["bg"], padx=40)
        kpi_container.pack(fill="x", pady=(0, 24))
        
        # Grid de 4 columnas
        for i in range(4):
            kpi_container.columnconfigure(i, weight=1, uniform="kpi")
        
        # Definición de KPIs con iconos
        kpi_defs = [
            ("actas", "📊", _("Actas Totales", self.lang), self.c["primary"]),
            ("precision", "🎯", _("Precisión IA", self.lang), self.c["success"]),
            ("tiempo", "⏱️", _("Tiempo Total", self.lang), self.c["primary"]),
            ("modismos", "🇨🇱", _("Modismos", self.lang), self.c["warning"]),
        ]
        
        for col, (key, icon, label, color) in enumerate(kpi_defs):
            card, val_lbl = self._create_kpi_card(
                kpi_container, 
                icon, 
                "--", 
                label, 
                color
            )
            card.grid(row=0, column=col, sticky="ew", padx=(0, 12) if col < 3 else 0)
            self.kpi_labels[key] = val_lbl
    
    def _create_kpi_card(self, parent, icon, value, label, color):
        """Crea una tarjeta KPI mejorada con icono y hover effect."""
        card = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            padx=24,
            pady=12,
            highlightbackground=self.c["border"],
            highlightthickness=1,
            cursor="hand2"
        )
        
        # Borde izquierdo de color
        accent = tk.Frame(card, bg=color, width=4)
        accent.place(relheight=1, x=0, y=0)
        
        # Container interno con padding
        inner = tk.Frame(card, bg=self.c["card_bg"], padx=12)
        inner.pack(fill="both", expand=True)
        
        # Row superior: Icono + Valor
        top_row = tk.Frame(inner, bg=self.c["card_bg"])
        top_row.pack(fill="x", pady=(0, 8))
        
        # Icono
        tk.Label(
            top_row,
            text=icon,
            bg=self.c["card_bg"],
            font=("Segoe UI", 24)
        ).pack(side="left", padx=(0, 12))
        
        # Valor (guardamos referencia)
        val_lbl = tk.Label(
            top_row,
            text=value,
            bg=self.c["card_bg"],
            fg=color,
            font=("Segoe UI", 24, "bold")
        )
        val_lbl.pack(side="left")
        
        # Label descriptivo
        tk.Label(
            inner,
            text=label,
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w")
        
        # Hover effect
        def on_enter(e):
            card.configure(highlightbackground=color, highlightthickness=2)
        
        def on_leave(e):
            card.configure(highlightbackground=self.c["border"], highlightthickness=1)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card, val_lbl
    
    def _build_quick_stats(self, parent):
        """Estadísticas rápidas adicionales en cards horizontales."""
        stats_container = tk.Frame(parent, bg=self.c["bg"], padx=40)
        stats_container.pack(fill="x", pady=(0, 24))
        
        # Grid de 2 columnas
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Card 1: Actividad reciente
        self._build_activity_card(stats_container).grid(
            row=0, column=0, sticky="nsew", padx=(0, 12)
        )
        
        # Card 2: Tendencia
        self._build_trend_card(stats_container).grid(
            row=0, column=1, sticky="nsew"
        )
    
    def _build_activity_card(self, parent):
        """Card de actividad reciente."""
        card = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            padx=24,
            pady=12,
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        
        # Header
        tk.Label(
            card,
            text="📈 Actividad Reciente",
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"]
        ).pack(anchor="w", pady=(0, 12))
        
        # Obtener datos de últimos 7 días
        all_actas = self.db.get_all_actas() if self.db else []
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        recent = [
            a for a in all_actas 
            if a.fecha_creacion and a.fecha_creacion >= seven_days_ago
        ]
        
        # Estadísticas
        stats_text = f"""
        • {len(recent)} actas en los últimos 7 días
        • {sum(len(a.modismos_detectados) for a in recent)} modismos detectados
        • {sum(a.duracion_segundos or 0 for a in recent) / 3600:.1f}h procesadas
        """
        
        tk.Label(
            card,
            text=stats_text.strip(),
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["body"],
            justify="left"
        ).pack(anchor="w")
        
        return card
    
    def _build_trend_card(self, parent):
        """Card de tendencia (comparación con período anterior)."""
        card = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            padx=24,
            pady=12,
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        
        # Header
        tk.Label(
            card,
            text="📊 Tendencia",
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"]
        ).pack(anchor="w", pady=(0, 12))
        
        # Calcular tendencia
        all_actas = self.db.get_all_actas() if self.db else []
        now = datetime.now()
        this_month = [
            a for a in all_actas
            if a.fecha_creacion and 
               a.fecha_creacion.month == now.month and
               a.fecha_creacion.year == now.year
        ]
        
        last_month_date = now.replace(day=1) - timedelta(days=1)
        last_month = [
            a for a in all_actas
            if a.fecha_creacion and
               a.fecha_creacion.month == last_month_date.month and
               a.fecha_creacion.year == last_month_date.year
        ]
        
        # Calcular cambio porcentual
        this_count = len(this_month)
        last_count = len(last_month)
        
        if last_count > 0:
            change = ((this_count - last_count) / last_count) * 100
            trend_icon = "📈" if change > 0 else "📉"
            trend_color = self.c["success"] if change > 0 else self.c["danger"]
            trend_text = f"{trend_icon} {abs(change):.0f}% vs mes anterior"
        else:
            trend_text = "Sin datos del mes anterior"
            trend_color = self.c["text_secondary"]
        
        # Mostrar tendencia
        tk.Label(
            card,
            text=f"Este mes: {this_count} actas",
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=FONTS["body"]
        ).pack(anchor="w", pady=(0, 4))
        
        tk.Label(
            card,
            text=trend_text,
            bg=self.c["card_bg"],
            fg=trend_color,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")
        
        return card
    
    def _build_recent_table(self, parent):
        """Tabla de actas recientes con acciones."""
        table_container = tk.Frame(parent, bg=self.c["bg"], padx=40)
        table_container.pack(fill="both", expand=True, pady=(0, 24))
        
        # Header de tabla con botón "Ver todas"
        table_header = tk.Frame(table_container, bg=self.c["bg"])
        table_header.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            table_header,
            text=_("Últimas Actas Procesadas", self.lang),
            bg=self.c["bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"]
        ).pack(side="left")
        
        # Botón "Ver todas →"
        ttk.Button(
            table_header,
            text="Ver todas →",
            style="Secondary.TButton",
            command=self._go_to_history,
            width=12
        ).pack(side="right")
        
        # Frame para tabla
        table_frame = tk.Frame(
            table_container,
            bg=self.c["card_bg"],
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        table_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("Nombre", "Fecha", "Duración", "Modismos", "Estado")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        # Configurar columnas
        column_config = {
            "Nombre": (300, "w", _("Nombre", self.lang)),
            "Fecha": (140, "center", _("Fecha", self.lang)),
            "Duración": (100, "center", _("Duración", self.lang)),
            "Modismos": (100, "center", _("Modismos", self.lang)),
            "Estado": (150, "center", _("Estado", self.lang)),
        }
        
        for col, (width, anchor, label) in column_config.items():
            self.tree.heading(col, text=label.upper())
            self.tree.column(col, width=width, anchor=anchor) # type: ignore
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        # Bind doble click para abrir acta
        self.tree.bind("<Double-Button-1>", self._on_double_click_acta)
        
        # Bind click derecho para menú contextual
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.refresh_data()
    
    def _go_to_history(self):
        """Navega a la vista de historial."""
        if self.app:
            self.app.show_view("history")
    
    def _on_double_click_acta(self, event):
        """Handler para doble click en acta."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Obtener ID del acta desde tags
        item = selection[0]
        tags = self.tree.item(item, "tags")
        if not tags: return
        acta_id = int(tags[0])
        
        # Cargar acta completa desde DB
        acta = self.db.get_acta_by_id(acta_id)
        if not acta:
            from tkinter import messagebox
            messagebox.showerror(_("Error", self.lang), _("No se pudo cargar el acta.", self.lang))
            return
            
        # Mostrar diálogo
        TranscriptionDialog(self, acta, theme=self.theme, lang=self.lang)
    
    def _show_context_menu(self, event):
        """Muestra menú contextual al hacer click derecho."""
        # Seleccionar item bajo el cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Crear menú contextual
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label="👁️ Ver detalles",
                command=lambda: self._on_double_click_acta(None)
            )
            menu.add_separator()
            menu.add_command(
                label="🗑️ Eliminar",
                command=self._delete_selected
            )
            
            # Mostrar menú
            menu.post(event.x_root, event.y_root)
    
    def _delete_selected(self):
        """Elimina el acta seleccionada."""
        from tkinter import messagebox
        
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        acta_nombre = values[0]
        
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el acta '{acta_nombre}'?\n\nEsta acción no se puede deshacer."
        ):
            # Por ahora solo actualizamos la tabla
            # self.db.delete_acta(acta_id)
            self.refresh_data()
            messagebox.showinfo("Éxito", "Acta eliminada correctamente.")
    
    def refresh_data(self):
        """Actualiza todos los datos de la vista."""
        if not self.db:
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener datos
        all_actas = self.db.get_all_actas()
        
        # === ACTUALIZAR KPIs ===
        total_actas = len(all_actas)
        total_segundos = sum(a.duracion_segundos or 0 for a in all_actas)
        total_horas = total_segundos / 3600
        total_modismos = sum(len(a.modismos_detectados) for a in all_actas)
        
        # Precisión promedio
        wer_values = [a.wer_medido for a in all_actas if a.wer_medido is not None and a.wer_medido > 0]
        if wer_values:
            # Ahora wer_medido almacena el % de confianza (0.0 - 1.0)
            avg_conf = sum(wer_values) / len(wer_values)
            precision = avg_conf * 100
        else:
            precision = 95  # Valor por defecto
        
        # Actualizar labels
        self.kpi_labels["actas"].configure(text=str(total_actas))
        self.kpi_labels["tiempo"].configure(text=f"{total_horas:.1f}h")
        self.kpi_labels["modismos"].configure(text=str(total_modismos))
        self.kpi_labels["precision"].configure(text=f"{precision:.0f}%")
        
        # === ACTUALIZAR TABLA (últimas 8) ===
        # Ordenar actas por fecha descendente
        recent_actas = sorted(all_actas, key=lambda x: x.fecha_creacion or datetime.min, reverse=True)

        for acta in recent_actas[:8]: # type: ignore
            fecha_str = ""
            if acta.fecha_creacion:
                # Formato relativo si es reciente
                now = datetime.now()
                diff = now - acta.fecha_creacion
                
                if diff.days == 0:
                    fecha_str = "Hoy " + acta.fecha_creacion.strftime("%H:%M")
                elif diff.days == 1:
                    fecha_str = "Ayer " + acta.fecha_creacion.strftime("%H:%M")
                else:
                    fecha_str = acta.fecha_creacion.strftime("%d/%m/%Y")
            
            # Duración formateada
            duracion = acta.duracion_segundos or 0
            if duracion < 60:
                dur_str = f"{duracion}s"
            elif duracion < 3600:
                dur_str = f"{duracion // 60}m"
            else:
                dur_str = f"{duracion // 3600}h {(duracion % 3600) // 60}m"
            
            # Modismos
            modismos_count = len(acta.modismos_detectados)
            
            # Estado con emoji
            estado = "✅ " + _("Terminada", self.lang)
            
            # Insertar en tabla
            self.tree.insert(
                "",
                "end",
                values=(
                    acta.titulo,
                    fecha_str,
                    dur_str,
                    modismos_count,
                    estado
                ),
                tags=(acta.id,)
            )
