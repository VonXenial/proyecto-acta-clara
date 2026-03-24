"""
Vista Configuración - ActaClara v1.2.1
Pantalla de configuración completa con categorías navegables:
  General · Audio · Modismos · Exportación · Almacenamiento · Avanzado
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.ui.styles import COLORS, FONTS, DIMENSIONS


# ── Definición de categorías ─────────────────────────────────
CATEGORIES = [
    ("general",     "📱", "General"),
    ("audio",       "🎙️",  "Audio y Transcripción"),
    ("modismos",    "🇨🇱", "Modismos"),
    ("export",      "📄", "Exportación"),
    ("storage",     "💾", "Almacenamiento"),
    ("advanced",    "⚙️",  "Avanzado"),
]


class ConfigView(tk.Frame):
    """Vista de configuración completa con navegación por categorías."""

    VIEW_NAME = "config"

    def __init__(self, parent, config_manager, on_save=None, theme="light", audio_ctrl=None):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["bg"])
        self.cfg = config_manager
        self.on_save = on_save
        self.audio_ctrl = audio_ctrl
        self.theme = theme

        self._init_vars()
        self._build()

    # ── Variables de configuración ───────────────────────────

    def _init_vars(self):
        get = self.cfg.get

        # General
        self.theme_var       = tk.StringVar(value=get("appearance",       "light"))
        self.font_size_var   = tk.StringVar(value=get("font_size",        "mediano"))
        self.lang_ui_var     = tk.StringVar(value=get("lang_ui",          "Español"))

        # Audio
        self.mic_var         = tk.StringVar(value=get("microphone",       "default"))
        self.lang_stt_var    = tk.StringVar(value=get("lang_stt",         "Español (Chile)"))
        self.quality_var     = tk.StringVar(value=get("audio_quality",    "Alta (16kHz)"))
        self.model_var       = tk.StringVar(value=get("stt_model",        "Mediano (balanceado)"))
        self.diarize_var     = tk.BooleanVar(value=get("diarize",         True))
        self.timestamps_var  = tk.BooleanVar(value=get("timestamps",      True))

        # Modismos
        self.auto_norm_var   = tk.BooleanVar(value=get("auto_normalize",  True))
        self.only_suggest_var= tk.BooleanVar(value=get("only_suggest",    False))
        self.highlight_var   = tk.StringVar(value=get("highlight_style",  "naranja"))
        self.tooltip_var     = tk.StringVar(value=get("tooltip_mode",     "tooltip"))

        # Exportación
        self.export_fmt_var  = tk.StringVar(value=get("export_format",    "DOCX"))
        self.incl_audio_var  = tk.BooleanVar(value=get("include_audio",   True))
        self.template_var    = tk.StringVar(value=get("doc_template",     "Corporativa formal"))
        self.export_dir_var  = tk.StringVar(value=get("export_dir",       ""))
        self.filename_var    = tk.StringVar(value=get("filename_pattern",  "{titulo}_{fecha}.docx"))

        # Almacenamiento
        self.backup_var      = tk.BooleanVar(value=get("auto_backup",     True))
        self.backup_freq_var = tk.StringVar(value=get("backup_freq",      "Semanal"))
        self.auto_delete_var = tk.BooleanVar(value=get("auto_delete",     False))
        self.delete_after_var= tk.StringVar(value=get("delete_after",     "6 meses"))

        # Avanzado
        self.proc_mode_var   = tk.StringVar(value=get("proc_mode",        "CPU"))
        self.threads_var     = tk.StringVar(value=get("threads",          "Auto"))
        self.telemetry_var   = tk.BooleanVar(value=get("telemetry",       True))
        self.offline_var     = tk.BooleanVar(value=get("offline_mode",    False))
        self.log_level_var   = tk.StringVar(value=get("log_level",        "Normal"))
        self.auto_update_var = tk.StringVar(value=get("auto_update",      "Buscar y notificar"))

    # ── Layout principal ─────────────────────────────────────

    def _build(self):
        # Header
        header = tk.Frame(self, bg=self.c["bg"], pady=24, padx=40)
        header.pack(fill="x")
        tk.Label(header, text="Configuración", bg=self.c["bg"],
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")

        # Franja horizontal: sidebar + panel
        content = tk.Frame(self, bg=self.c["bg"], padx=40)
        content.pack(fill="both", expand=True)

        self._build_cat_sidebar(content)
        self._build_settings_panel(content)

        # Botones de acción
        self._build_action_bar()

        # Mostrar primera categoría
        self._show_category("general")

    def _build_cat_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.c["card_bg"], width=200,
                           highlightbackground=self.c["border"], highlightthickness=1)
        sidebar.pack(side="left", fill="y", padx=(0, 16), pady=(0, 16))
        sidebar.pack_propagate(False)

        self._cat_btns = {}
        for cat_id, icon, label in CATEGORIES:
            row = tk.Frame(sidebar, bg=self.c["card_bg"], cursor="hand2")
            row.pack(fill="x")

            indicator = tk.Frame(row, bg=self.c["card_bg"], width=4)
            indicator.pack(side="left", fill="y")

            lbl = tk.Label(row, text=f"{icon}  {label}", bg=self.c["card_bg"],
                           fg=self.c["text_secondary"], font=FONTS["body"],
                           anchor="w", pady=12, padx=14)
            lbl.pack(side="left", fill="both", expand=True)

            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, c=cat_id: self._show_category(c))
                w.bind("<Enter>",    lambda e, r=row, l=lbl, ind=indicator: self._hover(r, l, ind, True))
                w.bind("<Leave>",    lambda e, r=row, l=lbl, ind=indicator: self._hover(r, l, ind, False))

            self._cat_btns[cat_id] = (row, lbl, indicator)

    def _build_settings_panel(self, parent):
        outer = tk.Frame(parent, bg=self.c["card_bg"],
                         highlightbackground=self.c["border"], highlightthickness=1)
        outer.pack(side="left", fill="both", expand=True, pady=(0, 16))

        # Scrollable interior
        canvas = tk.Canvas(outer, bg=self.c["card_bg"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._panel = tk.Frame(canvas, bg=self.c["card_bg"])
        self._panel_id = canvas.create_window((0, 0), window=self._panel, anchor="nw")

        self._panel.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._panel_id, width=e.width))

        # Mouse wheel
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _build_action_bar(self):
        bar = tk.Frame(self, bg=self.c["bg"], pady=16, padx=40)
        bar.pack(fill="x")
        ttk.Button(bar, text="Restablecer", style="Secondary.TButton",
                   command=self._reset_defaults).pack(side="left")
        ttk.Button(bar, text="💾  Guardar Cambios", style="Primary.TButton",
                   command=self._save).pack(side="right")

    # ── Cambio de categoría ──────────────────────────────────

    def _show_category(self, cat_id: str):
        # Limpiar panel
        for w in self._panel.winfo_children():
            w.destroy()

        # Resaltar botón activo
        for cid, (row, lbl, ind) in self._cat_btns.items():
            active = (cid == cat_id)
            bg = self.c["sidebar_active"] if active else self.c["card_bg"]
            fg = "white" if active else self.c["text_secondary"]
            row.configure(bg=bg)
            lbl.configure(bg=bg, fg=fg)
            ind.configure(bg=self.c["primary"] if active else self.c["card_bg"])

        # Renderizar sección
        builders = {
            "general":  self._sect_general,
            "audio":    self._sect_audio,
            "modismos": self._sect_modismos,
            "export":   self._sect_export,
            "storage":  self._sect_storage,
            "advanced": self._sect_advanced,
        }
        builders.get(cat_id, lambda: None)()

    # ── Helpers de UI ────────────────────────────────────────

    def _section(self, title: str) -> tk.Frame:
        """Agrega un título de sección y retorna un frame contenedor."""
        tk.Label(self._panel, text=title, bg=self.c["card_bg"],
                 fg=self.c["text_primary"], font=FONTS["heading"]
                 ).pack(anchor="w", padx=32, pady=(28, 4))
        sep = tk.Frame(self._panel, bg=self.c["border"], height=1)
        sep.pack(fill="x", padx=32, pady=(0, 16))
        frame = tk.Frame(self._panel, bg=self.c["card_bg"])
        frame.pack(fill="x", padx=32)
        return frame

    def _field_label(self, parent, text: str):
        tk.Label(parent, text=text, bg=self.c["card_bg"],
                 fg=self.c["text_secondary"], font=FONTS["small"]
                 ).pack(anchor="w", pady=(12, 2))

    def _radio_row(self, parent, var, options: list):
        """Fila de radios horizontales. options = [(value, label), ...]"""
        row = tk.Frame(parent, bg=self.c["card_bg"])
        row.pack(anchor="w", pady=(0, 4))
        for val, lbl in options:
            ttk.Radiobutton(row, text=lbl, variable=var, value=val).pack(side="left", padx=(0, 16))

    def _check(self, parent, text, var):
        ttk.Checkbutton(parent, text=text, variable=var).pack(anchor="w", pady=4)

    def _combo(self, parent, var, values, width=38):
        ttk.Combobox(parent, textvariable=var, values=values,
                     state="readonly", width=width).pack(anchor="w", pady=(0, 4))

    def _hover(self, row, lbl, ind, entering: bool):
        row_bg = self.c["sidebar_hover"] if entering else self.c["card_bg"]
        row.configure(bg=row_bg)
        lbl.configure(bg=row_bg)
        ind.configure(bg=row_bg)

    # ── Secciones de contenido ───────────────────────────────

    def _sect_general(self):
        # Apariencia
        f = self._section("Apariencia")
        self._field_label(f, "Tema:")
        self._radio_row(f, self.theme_var, [
            ("light", "☀️  Claro"), ("dark", "🌙  Oscuro")
        ])

        self._field_label(f, "Tamaño de fuente:")
        self._radio_row(f, self.font_size_var, [
            ("pequeño", "Pequeño"), ("mediano", "Mediano"),
            ("grande", "Grande"), ("extra_grande", "Extra grande")
        ])

        self._field_label(f, "Idioma de la interfaz:")
        self._combo(f, self.lang_ui_var, ["Español", "Inglés"], width=24)

    def _sect_audio(self):
        f = self._section("Audio y Transcripción")

        self._field_label(f, "Micrófono predeterminado:")
        mics = self._detect_mics()
        self._combo(f, self.mic_var, mics, width=46)

        self._field_label(f, "Idioma de transcripción por defecto:")
        self._combo(f, self.lang_stt_var, [
            "Español (Chile)", "Español (México)", "Español (España)",
            "Inglés (US)", "Inglés (UK)"
        ])

        self._field_label(f, "Calidad de audio:")
        self._combo(f, self.quality_var, [
            "Alta (16kHz, recomendado)", "Media (8kHz)", "Baja (para audios largos)"
        ])

        self._field_label(f, "Modelo de transcripción:")
        self._combo(f, self.model_var, [
            "Pequeño (rápido, menos preciso)",
            "Mediano (balanceado)  ← Recomendado",
            "Grande (lento, más preciso)"
        ])

        self._check(f, "Detección automática de hablantes (diarización)", self.diarize_var)
        self._check(f, "Agregar timestamps automáticamente", self.timestamps_var)

    def _sect_modismos(self):
        f = self._section("Normalización de Modismos")

        self._check(f, "Activar normalización al transcribir", self.auto_norm_var)
        self._check(f, "Solo sugerir, no aplicar automáticamente", self.only_suggest_var)

        self._field_label(f, "Resaltar modismos detectados:")
        self._combo(f, self.highlight_var, [
            "Resaltar en color naranja",
            "Solo subrayar",
            "No resaltar"
        ], width=36)

        self._field_label(f, "Mostrar sugerencias al detectar:")
        self._combo(f, self.tooltip_var, [
            "Mostrar tooltip interactivo",
            "Solo notificar en panel lateral",
            "No mostrar sugerencias"
        ], width=36)

        # Botones de diccionario
        btn_row = tk.Frame(f, bg=self.c["card_bg"])
        btn_row.pack(anchor="w", pady=(12, 4))
        ttk.Button(btn_row, text="🔄  Actualizar diccionario",
                   style="Secondary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="✏️  Crear diccionario personalizado",
                   style="Secondary.TButton").pack(side="left")

    def _sect_export(self):
        f = self._section("Exportación")

        self._field_label(f, "Formato de exportación por defecto:")
        self._combo(f, self.export_fmt_var, ["DOCX", "PDF", "Ambos (DOCX + PDF)"], width=30)

        self._check(f, "Adjuntar audio original en la carpeta de exportación", self.incl_audio_var)

        self._field_label(f, "Plantilla de documento:")
        self._combo(f, self.template_var, [
            "Corporativa formal", "Académica", "Minimalista"
        ], width=30)

        self._field_label(f, "Carpeta de guardado predeterminada:")
        dir_row = tk.Frame(f, bg=self.c["card_bg"])
        dir_row.pack(anchor="w", pady=(0, 4))
        ttk.Entry(dir_row, textvariable=self.export_dir_var, width=36).pack(side="left", padx=(0, 6))
        ttk.Button(dir_row, text="📂  Cambiar", style="Secondary.TButton",
                   command=self._pick_dir).pack(side="left")

        self._field_label(f, "Nomenclatura de archivos:")
        self._combo(f, self.filename_var, [
            "{titulo}_{fecha}.docx",
            "{fecha}_{titulo}.docx",
            "{proyecto}_{fecha}_{titulo}.docx"
        ], width=36)

    def _sect_storage(self):
        f = self._section("Almacenamiento")

        # Info de base de datos
        db_info = tk.Frame(f, bg=self.c["bg"], padx=12, pady=10,
                           highlightbackground=self.c["border"], highlightthickness=1)
        db_info.pack(fill="x", pady=(0, 12))
        tk.Label(db_info, text="Base de datos: SQLite (local)", bg=self.c["bg"],
                 fg=self.c["text_primary"], font=FONTS["body"]).pack(anchor="w")
        tk.Label(db_info, text="~/.actaclara/actaclara.db", bg=self.c["bg"],
                 fg=self.c["text_secondary"], font=FONTS["small"]).pack(anchor="w")

        self._check(f, "Activar copia de seguridad automática", self.backup_var)

        self._field_label(f, "Frecuencia de backup:")
        self._combo(f, self.backup_freq_var, ["Diario", "Semanal", "Mensual"], width=20)

        btn_row = tk.Frame(f, bg=self.c["card_bg"])
        btn_row.pack(anchor="w", pady=(8, 12))
        ttk.Button(btn_row, text="💾  Crear backup ahora",
                   style="Secondary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="📂  Restaurar desde backup",
                   style="Secondary.TButton").pack(side="left")

        self._check(f, "Eliminar actas antiguas automáticamente", self.auto_delete_var)
        self._field_label(f, "Eliminar actas después de:")
        self._combo(f, self.delete_after_var, ["3 meses", "6 meses", "1 año", "2 años"], width=20)

    def _sect_advanced(self):
        f = self._section("Rendimiento")

        self._field_label(f, "Modo de procesamiento:")
        self._combo(f, self.proc_mode_var, ["CPU (predeterminado)", "GPU (si disponible)"], width=30)

        self._field_label(f, "Hilos de procesamiento:")
        self._combo(f, self.threads_var, ["Auto (predeterminado)", "2 hilos", "4 hilos", "8 hilos"], width=24)

        f2 = self._section("Privacidad")
        self._check(f2, "Enviar estadísticas anónimas de uso para mejorar ActaClara", self.telemetry_var)
        self._check(f2, "Modo sin conexión (no actualizar diccionarios automáticamente)", self.offline_var)

        f3 = self._section("Logs y Actualizaciones")
        self._field_label(f3, "Nivel de logging:")
        self._combo(f3, self.log_level_var, [
            "Solo errores", "Normal (predeterminado)", "Detallado (debug)"
        ], width=28)

        btn_row = tk.Frame(f3, bg=self.c["card_bg"])
        btn_row.pack(anchor="w", pady=(8, 12))
        ttk.Button(btn_row, text="📋  Ver logs",
                   style="Secondary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="🗑️  Limpiar logs",
                   style="Secondary.TButton").pack(side="left")

        self._field_label(f3, "Actualizaciones automáticas:")
        self._combo(f3, self.auto_update_var, [
            "Buscar y notificar",
            "Descargar automáticamente",
            "No buscar actualizaciones"
        ], width=30)

    # ── Acciones ─────────────────────────────────────────────

    def _pick_dir(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de exportación")
        if folder:
            self.export_dir_var.set(folder)

    def _detect_mics(self) -> list:
        if self.audio_ctrl:
            try:
                return self.audio_ctrl.get_microphones() or ["Micrófono predeterminado"]
            except Exception:
                pass
        return ["Micrófono predeterminado", "Microsoft - Audio Input", "Realtek HD Audio"]

    def _save(self):
        """Persiste la configuración y notifica al orquestador."""
        mapping = {
            "appearance":       self.theme_var,
            "font_size":        self.font_size_var,
            "lang_ui":          self.lang_ui_var,
            "microphone":       self.mic_var,
            "lang_stt":         self.lang_stt_var,
            "audio_quality":    self.quality_var,
            "stt_model":        self.model_var,
            "diarize":          self.diarize_var,
            "timestamps":       self.timestamps_var,
            "auto_normalize":   self.auto_norm_var,
            "only_suggest":     self.only_suggest_var,
            "highlight_style":  self.highlight_var,
            "tooltip_mode":     self.tooltip_var,
            "export_format":    self.export_fmt_var,
            "include_audio":    self.incl_audio_var,
            "doc_template":     self.template_var,
            "export_dir":       self.export_dir_var,
            "filename_pattern": self.filename_var,
            "auto_backup":      self.backup_var,
            "backup_freq":      self.backup_freq_var,
            "auto_delete":      self.auto_delete_var,
            "delete_after":     self.delete_after_var,
            "proc_mode":        self.proc_mode_var,
            "threads":          self.threads_var,
            "telemetry":        self.telemetry_var,
            "offline_mode":     self.offline_var,
            "log_level":        self.log_level_var,
            "auto_update":      self.auto_update_var,
        }
        for key, var in mapping.items():
            self.cfg.set(key, var.get())

        messagebox.showinfo("Configuración guardada",
                            "Los cambios se han guardado correctamente.\n"
                            "Algunos ajustes se aplicarán al reiniciar la app.")
        if self.on_save:
            self.on_save()

    def _reset_defaults(self):
        if not messagebox.askyesno("Restablecer configuración",
                                   "¿Restablecer todos los valores a su estado predeterminado?"):
            return

        defaults = {
            "appearance": "light", "font_size": "mediano", "lang_ui": "Español",
            "microphone": "default", "lang_stt": "Español (Chile)",
            "audio_quality": "Alta (16kHz, recomendado)",
            "stt_model": "Mediano (balanceado)  ← Recomendado",
            "diarize": True, "timestamps": True,
            "auto_normalize": True, "only_suggest": False,
            "highlight_style": "Resaltar en color naranja",
            "tooltip_mode": "Mostrar tooltip interactivo",
            "export_format": "DOCX", "include_audio": True,
            "doc_template": "Corporativa formal",
            "export_dir": "", "filename_pattern": "{titulo}_{fecha}.docx",
            "auto_backup": True, "backup_freq": "Semanal",
            "auto_delete": False, "delete_after": "6 meses",
            "proc_mode": "CPU (predeterminado)", "threads": "Auto (predeterminado)",
            "telemetry": True, "offline_mode": False,
            "log_level": "Normal (predeterminado)",
            "auto_update": "Buscar y notificar",
        }
        for key, val in defaults.items():
            self.cfg.set(key, val)

        self._init_vars()
        self._show_category("general")
        messagebox.showinfo("Completado", "Configuración restablecida a los valores predeterminados.")
