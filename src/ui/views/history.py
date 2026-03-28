"""
Vista de Historial Profesional - ActaClara v1.4
Incluye: Búsqueda, Filtros, Preview, Acciones, Estadísticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Literal # type: ignore
from src.ui.styles import COLORS, FONTS, DIMENSIONS # type: ignore
from src.database.db_manager import DBManager # type: ignore
from src.utils.i18n import translate as _ # type: ignore
from src.models.acta import Acta # type: ignore
from src.config import RECORDINGS_DIR # type: ignore
import os


class TranscriptionDialog(tk.Toplevel):
    """Ventana emergente para visualizar la transcripción completa."""
    def __init__(self, parent, acta, theme="light", lang="Español"):
        super().__init__(parent)
        self.c = COLORS[theme]
        self.lang = lang
        self.acta = acta
        
        self.title(_("Visualizador de Transcripción", self.lang))
        self.geometry("900x700")
        self.configure(bg=self.c["bg"])
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._build()
        
    def _build(self):
        # Header
        header = tk.Frame(self, bg=self.c["bg"], pady=25, padx=40)
        header.pack(fill="x")
        
        tk.Label(
            header, 
            text=self.acta.titulo,
            bg=self.c["bg"],
            fg=self.c["primary"],
            font=FONTS["title"],
            wraplength=800,
            justify="left"
        ).pack(anchor="w")
        
        fecha_str = self.acta.fecha_creacion.strftime("%d/%m/%Y %H:%M") if self.acta.fecha_creacion else "--"
        duracion_str = f"{self.acta.duracion_segundos}s" if self.acta.duracion_segundos else ""
        
        meta_text = f"{_('Fecha', self.lang)}: {fecha_str}  |  {_('Duración', self.lang)}: {duracion_str}"
        tk.Label(
            header,
            text=meta_text,
            bg=self.c["bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", pady=(5, 0))
        
        # Separador decorativo
        sep = tk.Frame(self, height=2, bg=self.c["primary"])
        sep.pack(fill="x", padx=40)
        
        # Contenedor de texto
        container = tk.Frame(
            self, 
            bg=self.c["card_bg"],
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        container.pack(fill="both", expand=True, padx=40, pady=25)
        
        # Scrollbar y Texto
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")
        
        text_area = tk.Text(
            container,
            wrap="word",
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=("Segoe UI", 12),
            padx=30,
            pady=30,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            spacing2=5
        )
        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Cargar contenido
        content = self.acta.transcripcion_texto or _("(Sin transcripción disponible)", self.lang)
        text_area.insert("1.0", content)
        text_area.config(state="disabled") # Solo lectura
        
        # Footer con botón cerrar
        footer = tk.Frame(self, bg=self.c["bg"], pady=20)
        footer.pack(fill="x")
        
        ttk.Button(
            footer,
            text=_("Cerrar", self.lang),
            command=self.destroy,
            width=20
        ).pack()


class HistoryView(tk.Frame):
    """Vista de historial de actas con funcionalidades avanzadas."""
    
    VIEW_NAME = "history"
    
    def __init__(self, parent, db_manager, theme="light", app=None, lang="Español"):
        self.c = COLORS[theme]
        self.lang = lang
        super().__init__(parent, bg=self.c["bg"])
        
        self.db: DBManager = db_manager # type: ignore
        self.app = app  # Referencia a MainWindow para navegación
        
        # Declaración de atributos para el linter
        self.tree: ttk.Treeview = None # type: ignore
        self.count_label: tk.Label = None # type: ignore
        self.preview_container: tk.Frame = None # type: ignore
        self.btn_view: ttk.Button = None # type: ignore
        self.btn_export: ttk.Button = None # type: ignore
        self.btn_delete: ttk.Button = None # type: ignore
        
        self.selected_acta_id: Optional[int] = None
        
        # Atributos de estadísticas
        self.stat_actas_val: tk.Label = None # type: ignore
        self.stat_horas_val: tk.Label = None # type: ignore
        self.stat_modismos_val: tk.Label = None # type: ignore
        self.preview_canvas: tk.Canvas = None # type: ignore
        self._canvas_window: int = 0
        
        self.search_var = tk.StringVar()
        
        self.filter_lang_var = tk.StringVar(value=_("Todos", self.lang))
        self.filter_date_var = tk.StringVar(value=_("Todos", self.lang))
        
        self._build()

        # Configurar traces DESPUÉS de construir la UI para evitar race conditions
        self.search_var.trace("w", lambda *args: self._apply_filters())
        self.filter_lang_var.trace("w", lambda *args: self._apply_filters())
        self.filter_date_var.trace("w", lambda *args: self._apply_filters())
    
    def _build(self):
        """Construye la vista completa."""
        self._build_header()
        self._build_stats_bar()
        self._build_filters_bar()
        self._build_action_bar()
        self._build_body()
    
    def _build_header(self):
        """Header con título y botón de limpiar historial."""
        header = tk.Frame(self, bg=self.c["bg"], pady=20, padx=40)
        header.pack(fill="x")
        
        # Título
        tk.Label(
            header,
            text=_("Historial de Actas", self.lang),
            bg=self.c["bg"],
            fg=self.c["text_primary"],
            font=FONTS["title"]
        ).pack(side="left")
        
        # Botón limpiar historial
        ttk.Button(
            header,
            text=_("Limpiar Todo", self.lang),
            style="Secondary.TButton",
            command=self._clear_all_history,
            width=15
        ).pack(side="right")
    
    def _build_stats_bar(self):
        """Barra de estadísticas rápidas."""
        stats_frame = tk.Frame(self, bg=self.c["bg"], padx=40)
        stats_frame.pack(fill="x", pady=(0, 16))
        
        # Obtener estadísticas
        all_actas = self.db.get_all_actas()
        total_actas = len(all_actas)
        total_horas = sum(a.duracion_segundos or 0 for a in all_actas) / 3600
        total_modismos = sum(len(a.modismos_detectados) for a in all_actas)
        
        # Cards de estadísticas
        self.stat_actas_val = self._create_stat_card(stats_frame, str(total_actas), _("Actas procesadas", self.lang), self.c["primary"])
        self.stat_actas_val.master.pack(side="left", fill="x", expand=True, padx=(0, 12)) # type: ignore
        
        self.stat_horas_val = self._create_stat_card(stats_frame, f"{total_horas:.1f}h", _("Horas transcritas", self.lang), self.c["success"])
        self.stat_horas_val.master.pack(side="left", fill="x", expand=True, padx=(0, 12)) # type: ignore
        
        self.stat_modismos_val = self._create_stat_card(stats_frame, str(total_modismos), _("Modismos detectados", self.lang), self.c["warning"])
        self.stat_modismos_val.master.pack(side="left", fill="x", expand=True, padx=(0, 12)) # type: ignore
    
    def _create_stat_card(self, parent, value, label, color):
        """Crea una tarjeta de estadística y devuelve el label del valor."""
        card = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            padx=20,
            pady=16,
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        # Borde izquierdo de color
        accent = tk.Frame(card, bg=color, width=4)
        accent.place(relheight=1, x=0, y=0)
        
        # Valor (Guardamos referencia)
        val_lbl = tk.Label(
            card,
            text=value,
            bg=self.c["card_bg"],
            fg=color,
            font=("Segoe UI", 24, "bold")
        )
        val_lbl.pack(anchor="w", padx=(12, 0))
        
        # Label
        tk.Label(
            card,
            text=label,
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", padx=(12, 0))
        
        return val_lbl
    
    def _update_stats(self):
        """Actualiza los valores de las tarjetas de estadísticas."""
        all_actas = self.db.get_all_actas()
        total_actas = len(all_actas)
        total_horas = sum(a.duracion_segundos or 0 for a in all_actas) / 3600
        total_modismos = sum(len(a.modismos_detectados) for a in all_actas)
        
        if self.stat_actas_val:
            self.stat_actas_val.configure(text=str(total_actas))
        if self.stat_horas_val:
            self.stat_horas_val.configure(text=f"{total_horas:.1f}h")
        if self.stat_modismos_val:
            self.stat_modismos_val.configure(text=str(total_modismos))
    
    def _build_filters_bar(self):
        """Barra de filtros y búsqueda."""
        filter_frame = tk.Frame(
            self,
            bg=self.c["card_bg"],
            padx=30,
            pady=12,
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        filter_frame.pack(fill="x", padx=40, pady=(0, 16))
        
        # Búsqueda
        search_container = tk.Frame(filter_frame, bg=self.c["card_bg"])
        search_container.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            search_container,
            text="🔍",
            bg=self.c["card_bg"],
            font=("Segoe UI", 14)
        ).pack(side="left", padx=(0, 8))
        
        search_entry = ttk.Entry(
            search_container,
            textvariable=self.search_var,
            font=FONTS["body"],
            width=40
        )
        search_entry.pack(side="left", fill="x", expand=True)
        placeholder = _("Buscar por título...", self.lang)
        search_entry.insert(0, placeholder)
        
        # Bind para placeholder
        def on_focus_in(event):
            if search_entry.get() == placeholder:
                search_entry.delete(0, tk.END)
        
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, placeholder)
        
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        
        # Filtros
        tk.Frame(filter_frame, width=20, bg=self.c["card_bg"]).pack(side="left")
        
        tk.Label(
            filter_frame,
            text=_("Idioma:", self.lang),
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(side="left", padx=(0, 8))
        
        lang_values = [_("Todos", self.lang), _("Español", self.lang), _("Inglés", self.lang)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_lang_var,
            values=lang_values,
            state="readonly",
            width=12
        ).pack(side="left", padx=(0, 16))
        
        tk.Label(
            filter_frame,
            text=_("Fecha:", self.lang),
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        ).pack(side="left", padx=(0, 8))
        
        date_values = [_("Todos", self.lang), _("Hoy", self.lang), _("Esta semana", self.lang), _("Este mes", self.lang)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_date_var,
            values=date_values,
            state="readonly",
            width=12
        ).pack(side="left")
        
        # Vincular cambios de filtro (movido a __init__)
        pass
    
    def _build_body(self):
        """Cuerpo con tabla de actas."""
        body = tk.Frame(self, bg=self.c["bg"])
        body.pack(fill="both", expand=True, padx=40, pady=(0, 16))
        
        # Configurar grid (2 columnas)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        
        # Panel izquierdo: Tabla
        self._build_table(body)
        
        # Panel derecho: Preview
        self._build_preview_panel(body)
    
    def _build_table(self, parent):
        """Tabla de actas."""
        table_frame = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            padx=0,
            pady=0,
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        # Header de tabla
        table_header = tk.Frame(table_frame, bg=self.c["card_bg"], pady=12, padx=20)
        table_header.pack(fill="x")
        
        tk.Label(
            table_header,
            text=_("Lista de Actas", self.lang),
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"]
        ).pack(side="left")
        
        # Contador de resultados
        self.count_label = tk.Label(
            table_header,
            text="",
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["small"]
        )
        self.count_label.pack(side="right")
        
        # Treeview
        internal_cols = ("ID", "Título", "Fecha", "Duración", "Idioma", "Modismos")
        self.tree = ttk.Treeview(
            table_frame,
            columns=internal_cols,
            show="headings",
            height=15
        )
        
        # Configurar columnas
        column_config = {
            "ID": (60, "center", _("ID", self.lang)),
            "Título": (280, "w", _("Título", self.lang)),
            "Fecha": (140, "center", _("Fecha", self.lang)),
            "Duración": (100, "center", _("Duración", self.lang)),
            "Idioma": (100, "center", _("Idioma", self.lang)),
            "Modismos": (100, "center", _("Modismos", self.lang)),
        }
        
        for col_id, (width, anchor, label) in column_config.items():
            self.tree.heading(col_id, text=label.upper())
            self.tree.column(col_id, width=width, anchor=anchor) # type: ignore
        
        # Scroll "Invisible" (sin widget scrollbar visible)
        self.tree.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Bind MouseWheel para la Tabla con gestión de foco
        def _on_mousewheel_table(event):
            if event.num == 4: self.tree.yview_scroll(-1, "units")
            elif event.num == 5: self.tree.yview_scroll(1, "units")
            else: self.tree.yview_scroll(int(-1*(event.delta/120)), "units")

        table_frame.bind("<Enter>", lambda e: self.tree.bind_all("<MouseWheel>", _on_mousewheel_table))
        table_frame.bind("<Leave>", lambda e: self.tree.unbind_all("<MouseWheel>"))

        # Bind selección
        self.tree.bind("<<TreeviewSelect>>", self._on_select_acta)
    
    def _build_preview_panel(self, parent):
        """Panel de preview de acta seleccionada con scroll invisible."""
        preview_outer = tk.Frame(
            parent,
            bg=self.c["card_bg"],
            highlightbackground=self.c["border"],
            highlightthickness=1
        )
        preview_outer.grid(row=0, column=1, sticky="nsew")
        
        # Header (Fixed)
        header = tk.Frame(preview_outer, bg=self.c["card_bg"], padx=20, pady=20)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text=_("Vista Previa", self.lang),
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"]
        ).pack(anchor="w")

        # Área de Scroll (Canvas sin Scrollbar visible)
        container = tk.Frame(preview_outer, bg=self.c["card_bg"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.preview_canvas = tk.Canvas(
            container, 
            bg=self.c["card_bg"], 
            highlightthickness=0
        )
        
        self.preview_container = tk.Frame(self.preview_canvas, bg=self.c["card_bg"])
        self.preview_canvas.pack(side="left", fill="both", expand=True)
        
        # Crear ventana en canvas para el frame
        self._canvas_window = self.preview_canvas.create_window(
            (0, 0), window=self.preview_container, anchor="nw"
        )
        
        # Ajustar ancho del frame al del canvas automáticamente
        self.preview_canvas.bind("<Configure>", lambda e: self.preview_canvas.itemconfig(self._canvas_window, width=e.width))
        
        # Actualizar región de scroll cuando cambie el contenido
        self.preview_container.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))
        
        # Bind MouseWheel para el Preview con gestión de foco (Enter/Leave)
        def _on_mousewheel_preview(event):
            if event.num == 4: self.preview_canvas.yview_scroll(-1, "units")
            elif event.num == 5: self.preview_canvas.yview_scroll(1, "units")
            else: self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_preview_scroll(event):
            self.preview_canvas.bind_all("<MouseWheel>", _on_mousewheel_preview)
            self.preview_canvas.bind_all("<Button-4>", _on_mousewheel_preview)
            self.preview_canvas.bind_all("<Button-5>", _on_mousewheel_preview)

        def _unbind_preview_scroll(event):
            self.preview_canvas.unbind_all("<MouseWheel>")
            self.preview_canvas.unbind_all("<Button-4>")
            self.preview_canvas.unbind_all("<Button-5>")

        # Vincular eventos de entrada/salida para el área de preview
        preview_outer.bind("<Enter>", _bind_preview_scroll)
        preview_outer.bind("<Leave>", _unbind_preview_scroll)

        # Mensaje inicial
        tk.Label(
            self.preview_container,
            text=_("Selecciona un acta para ver detalles", self.lang).replace(" ", "\n", 3),
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["body"],
            justify="center"
        ).pack(expand=True, pady=100)
    
    def _build_action_bar(self):
        """Barra de acciones inferiores."""
        action_frame = tk.Frame(self, bg=self.c["bg"], padx=40, pady=16)
        action_frame.pack(side="bottom", fill="x")
        
        # Botones de acción (deshabilitados hasta seleccionar)
        self.btn_view = ttk.Button(
            action_frame,
            text=_("👁️ Ver Completa", self.lang),
            style="Secondary.TButton",
            command=self._view_acta,
            state="disabled",
            width=18
        )
        self.btn_view.pack(side="left", padx=(0, 8))
        
        self.btn_export = ttk.Button(
            action_frame,
            text=_("📄 Exportar", self.lang),
            style="Secondary.TButton",
            command=self._export_acta,
            state="disabled",
            width=18
        )
        self.btn_export.pack(side="left", padx=(0, 8))
        
        self.btn_delete = ttk.Button(
            action_frame,
            text=_("🗑️ Eliminar", self.lang),
            style="Secondary.TButton",
            command=self._delete_acta,
            state="disabled",
            width=18
        )
        self.btn_delete.pack(side="left", padx=(0, 8))
        
        ttk.Button(
            action_frame,
            text=_("📁 Abrir Carpeta de Audios", self.lang),
            style="Secondary.TButton",
            command=self._open_audio_folder,
            width=24
        ).pack(side="right")
    
    def refresh_data(self):
        """Recarga los datos de la base de datos."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener todas las actas
        actas = self.db.get_all_actas()
        
        # Insertar en tabla
        for acta in actas:
            fecha_str = ""
            if acta.fecha_creacion:
                fecha_str = acta.fecha_creacion.strftime("%d/%m/%Y %H:%M")
            
            duracion_str = self._format_duration(acta.duracion_segundos or 0)
            modismos_count = len(acta.modismos_detectados)
            
            self.tree.insert(
                "",
                "end",
                values=(
                    acta.id,
                    acta.titulo,
                    fecha_str,
                    duracion_str,
                    acta.idioma or "N/A",
                    modismos_count
                ),
                tags=(acta.id,)
            )
        
        # Actualizar estadísticas
        self._update_stats()
        
        # Actualizar contador
        found_txt = _("actas encontradas", self.lang)
        self.count_label.configure(text=f"{len(actas)} {found_txt}")
    
    def _apply_filters(self):
        """Aplica los filtros de búsqueda."""
        # Obtener criterios
        search_text = self.search_var.get().lower()
        placeholder = _("Buscar por título...", self.lang).lower()
        if search_text == placeholder:
            search_text = ""
        
        lang_filter = self.filter_lang_var.get()
        date_filter = self.filter_date_var.get()
        all_txt = _("Todos", self.lang)
        
        # Obtener todas las actas
        all_actas = self.db.get_all_actas()
        
        # Filtrar
        filtered = []
        for acta in all_actas:
            # Filtro de búsqueda
            if search_text and search_text not in acta.titulo.lower():
                continue
            
            # Filtro de idioma
            # Mapear traducción a valor interno si es necesario, 
            # pero el acta.idioma parece venir como "Español" o "Inglés" según db_manager
            if lang_filter != all_txt and acta.idioma != lang_filter:
                # Intento de match con traducciones inversas
                es_txt = _("Español", self.lang)
                en_txt = _("Inglés", self.lang)
                target = ""
                if lang_filter == es_txt: target = "Español"
                elif lang_filter == en_txt: target = "Inglés"
                
                if acta.idioma != target and acta.idioma != lang_filter:
                    continue
                
            # Filtro de fecha
            if date_filter != all_txt:
                # Mapeo de traducción a tipo de filtro
                f_type = ""
                if date_filter == _("Hoy", self.lang): f_type = "Hoy"
                elif date_filter == _("Esta semana", self.lang): f_type = "Esta semana"
                elif date_filter == _("Este mes", self.lang): f_type = "Este mes"
                
                if not self._matches_date_filter(acta.fecha_creacion, f_type):
                    continue
            
            filtered.append(acta)
        
        # Actualizar tabla (con guard para evitar errores durante construcción)
        if not self.tree:
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for acta in filtered:
            fecha_str = ""
            if acta.fecha_creacion:
                fecha_str = acta.fecha_creacion.strftime("%d/%m/%Y %H:%M")
            
            duracion_str = self._format_duration(acta.duracion_segundos or 0)
            modismos_count = len(acta.modismos_detectados)
            
            self.tree.insert(
                "",
                "end",
                values=(
                    acta.id,
                    acta.titulo,
                    fecha_str,
                    duracion_str,
                    acta.idioma or "N/A",
                    modismos_count
                ),
                tags=(acta.id,)
            )
        
        # Actualizar contador
        de_txt = _("de", self.lang)
        actas_txt = _("actas", self.lang)
        self.count_label.configure(text=f"{len(filtered)} {de_txt} {len(all_actas)} {actas_txt}")
    
    def _matches_date_filter(self, fecha, filter_type):
        """Verifica si una fecha coincide con el filtro."""
        if not fecha:
            return False
        
        now = datetime.now()
        
        if filter_type == "Hoy":
            return fecha.date() == now.date()
        
        elif filter_type == "Esta semana":
            start_week = now - timedelta(days=now.weekday())
            return fecha >= start_week
        
        elif filter_type == "Este mes":
            return fecha.month == now.month and fecha.year == now.year
        
        return True
    
    def _on_select_acta(self, event):
        """Handler cuando se selecciona un acta."""
        selection = self.tree.selection()
        if not selection:
            self.selected_acta_id = None
            self._disable_action_buttons()
            self._clear_preview()
            return
        
        # Obtener ID del acta
        item = selection[0]
        values = self.tree.item(item, "values")
        self.selected_acta_id = int(values[0])
        
        # Habilitar botones
        self._enable_action_buttons()
        
        # Actualizar preview
        self._update_preview(self.selected_acta_id)
    
    def _update_preview(self, acta_id):
        """Actualiza el panel de preview."""
        # Limpiar preview
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # Obtener acta
        acta = self.db.get_acta_by_id(acta_id)
        if not acta:
            return
        
        # Información básica
        info_frame = tk.Frame(self.preview_container, bg=self.c["card_bg"])
        info_frame.pack(fill="x", pady=(0, 16))
        
        # Título
        tk.Label(
            info_frame,
            text=acta.titulo,
            bg=self.c["card_bg"],
            fg=self.c["text_primary"],
            font=("Segoe UI", 12, "bold"),
            wraplength=250,
            justify="left"
        ).pack(anchor="w", pady=(0, 8))
        
        # Detalles
        details = [
            ("📅 " + _("Fecha:", self.lang), acta.fecha_creacion.strftime("%d/%m/%Y %H:%M") if acta.fecha_creacion else "N/A"),
            ("⏱️ " + _("Duración", self.lang), self._format_duration(acta.duracion_segundos or 0)),
            ("🌍 " + _("Idioma", self.lang), acta.idioma or "N/A"),
            ("📊 WER:", f"{acta.wer_medido:.1f}%" if acta.wer_medido else "N/A"),
            ("🇨🇱 " + _("Modismos", self.lang), str(len(acta.modismos_detectados))),
        ]
        
        for label, value in details:
            row = tk.Frame(info_frame, bg=self.c["card_bg"])
            row.pack(fill="x", pady=2)
            
            tk.Label(
                row,
                text=label,
                bg=self.c["card_bg"],
                fg=self.c["text_secondary"],
                font=FONTS["small"],
                width=15,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                row,
                text=value,
                bg=self.c["card_bg"],
                fg=self.c["text_primary"],
                font=FONTS["body"],
                anchor="w"
            ).pack(side="left")
        
        # Separador
        ttk.Separator(
            self.preview_container,
            orient="horizontal"
        ).pack(fill="x", pady=16)
        
        # Modismos detectados
        if acta.modismos_detectados:
            tk.Label(
                self.preview_container,
                text=_("Modismos detectados:", self.lang),
                bg=self.c["card_bg"],
                fg=self.c["text_primary"],
                font=FONTS["heading"]
            ).pack(anchor="w", pady=(0, 8))
            
            # Mostrar TODOS los modismos
            for modismo in acta.modismos_detectados:
                mod_frame = tk.Frame(
                    self.preview_container,
                    bg=self.c["warning_light"],
                    padx=8,
                    pady=6
                )
                mod_frame.pack(fill="x", pady=4)
                
                tk.Label(
                    mod_frame,
                    text=f'"{modismo.expresion_original}"',
                    bg=self.c["warning_light"],
                    fg=self.c["warning"],
                    font=("Segoe UI", 9, "bold")
                ).pack(anchor="w")
                
                tk.Label(
                    mod_frame,
                    text=f"→ {modismo.expresion_normalizada}",
                    bg=self.c["warning_light"],
                    fg=self.c["text_secondary"],
                    font=FONTS["small"]
                ).pack(anchor="w")
            
            # Espaciador final para el scroll
            tk.Frame(self.preview_container, height=40, bg=self.c["card_bg"]).pack(fill="x")
    
    def _clear_preview(self):
        """Limpia el panel de preview."""
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.preview_container,
            text=_("Selecciona un acta para ver detalles", self.lang).replace(" ", "\n", 3),
            bg=self.c["card_bg"],
            fg=self.c["text_secondary"],
            font=FONTS["body"],
            justify="center"
        ).pack(expand=True)
    
    def _enable_action_buttons(self):
        """Habilita botones de acción."""
        self.btn_view.configure(state="normal")
        self.btn_export.configure(state="normal")
        self.btn_delete.configure(state="normal")
    
    def _disable_action_buttons(self):
        """Deshabilita botones de acción."""
        self.btn_view.configure(state="disabled")
        self.btn_export.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
    
    def _open_audio_folder(self):
        """Abre la carpeta de grabaciones en el explorador de archivos."""
        if not os.path.exists(RECORDINGS_DIR):
            os.makedirs(RECORDINGS_DIR, exist_ok=True)
            
        try:
            os.startfile(RECORDINGS_DIR) # type: ignore
        except Exception as e:
            messagebox.showerror(_("Error", self.lang), f"No se pudo abrir la carpeta:\n{e}")

    def _view_acta(self):
        """Abre la vista completa del acta."""
        if not self.selected_acta_id:
            return
        
        # Cargar acta completa desde DB
        acta = self.db.get_acta_by_id(self.selected_acta_id)
        if not acta:
            messagebox.showerror(_("Error", self.lang), _("No se pudo cargar el acta.", self.lang))
            return
            
        # Detectar el tema actual
        theme_name = "light"
        if hasattr(self.app, "theme"):
            theme_name = self.app.theme
            
        # Mostrar diálogo
        TranscriptionDialog(self, acta, theme=theme_name, lang=self.lang)
    
    def _export_acta(self):
        """Exporta el acta seleccionada."""
        if not self.selected_acta_id:
            return
        
        # Navegar a vista de exportación con acta pre-cargada
        if self.app:
            self.app.show_view("export", context={"acta_id": self.selected_acta_id})
    
    def _delete_acta(self):
        """Elimina el acta seleccionada."""
        if not self.selected_acta_id:
            return
        
        acta = self.db.get_acta_by_id(self.selected_acta_id)
        
        if messagebox.askyesno(
            _("Confirmar eliminación", self.lang),
            _("¿Estás seguro de eliminar el acta", self.lang) + f" '{acta.titulo}'?\n\n" +
            _("Esta acción no se puede deshacer.", self.lang)
        ):
            try:
                self.db.delete_acta(self.selected_acta_id)
                messagebox.showinfo(_("Éxito", self.lang), _("Acta eliminada correctamente.", self.lang))
                self.refresh_data()
            except Exception as e:
                messagebox.showerror(_("Error", self.lang), _("No se pudo eliminar el acta:", self.lang) + f"\n{e}")
    
    def _clear_all_history(self):
        """Limpia todo el historial."""
        if messagebox.askyesno(
            _("⚠️ Confirmar limpieza total", self.lang),
            _("¿Estás seguro de eliminar TODAS las actas del historial?", self.lang) + "\n\n" +
            _("Esta acción es IRREVERSIBLE y eliminará:", self.lang) + "\n" +
            "• " + _("Todas las actas procesadas", self.lang) + "\n" +
            "• " + _("Todos los modismos detectados", self.lang) + "\n" +
            "• " + _("Todos los registros de la base de datos", self.lang) + "\n\n" +
            _("Los archivos de audio NO se eliminarán.", self.lang)
        ):
            # Pedir confirmación adicional de seguridad
            try:
                self.db.clear_history()
                messagebox.showinfo(
                    _("Historial limpiado", self.lang),
                    _("Todas las actas han sido eliminadas de la base de datos.", self.lang)
                )
                self.refresh_data()
            except Exception as e:
                messagebox.showerror(
                    _("Error", self.lang),
                    _("No se pudo limpiar el historial:", self.lang) + f"\n{e}"
                )
    
    def _format_duration(self, seconds: int) -> str:
        """Formatea duración en formato legible."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}m {secs}s"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m"
