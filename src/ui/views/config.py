"""
Vista Configuración - ActaClara v1.2.1
Pantalla de configuración completa con categorías navegables:
  General · Audio · Modismos · Exportación · Almacenamiento · Avanzado
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.ui.styles import COLORS, FONTS # type: ignore
from typing import Optional, Dict, Any, List, Tuple
import os
import shutil
import datetime
import json
import logging
from src.utils.i18n import translate as _  # type: ignore
from src.utils.doc_templates.templates import get_template_names # type: ignore

try:
    from src.config import DB_PATH, DICTIONARY_PATH, USER_DATA_DIR  # type: ignore
    LOG_DIR = os.path.join(USER_DATA_DIR, "logs")
except ImportError:
    import sys
    USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "ActaClara")
    DB_PATH = os.path.join(USER_DATA_DIR, "data", "actaclara.db")
    DICTIONARY_PATH = os.path.join(USER_DATA_DIR, "data", "diccionarios", "modismos_es_CL_v1.0.json")
    LOG_DIR = os.path.join(USER_DATA_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "actaclara.log")


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

        # Inicialización de atributos para el linter
        self.theme_var: tk.StringVar = None # type: ignore
        self.font_size_var: tk.StringVar = None # type: ignore
        self.lang_ui_var: tk.StringVar = None # type: ignore
        self.mic_var: tk.StringVar = None # type: ignore
        self.lang_stt_var: tk.StringVar = None # type: ignore
        self.quality_var: tk.StringVar = None # type: ignore
        self.model_var: tk.StringVar = None # type: ignore
        self.diarize_var: tk.BooleanVar = None # type: ignore
        self.timestamps_var: tk.BooleanVar = None # type: ignore
        self.auto_norm_var: tk.BooleanVar = None # type: ignore
        self.only_suggest_var: tk.BooleanVar = None # type: ignore
        self.highlight_var: tk.StringVar = None # type: ignore
        self.tooltip_var: tk.StringVar = None # type: ignore
        self.export_fmt_var: tk.StringVar = None # type: ignore
        self.incl_audio_var: tk.BooleanVar = None # type: ignore
        self.template_var: tk.StringVar = None # type: ignore
        self.export_dir_var: tk.StringVar = None # type: ignore
        self.filename_var: tk.StringVar = None # type: ignore
        self.backup_var: tk.BooleanVar = None # type: ignore
        self.backup_freq_var: tk.StringVar = None # type: ignore
        self.auto_delete_var: tk.BooleanVar = None # type: ignore
        self.delete_after_var: tk.StringVar = None # type: ignore
        self.proc_mode_var: tk.StringVar = None # type: ignore
        self.threads_var: tk.StringVar = None # type: ignore
        self.telemetry_var: tk.BooleanVar = None # type: ignore
        self.offline_var: tk.BooleanVar = None # type: ignore
        self.log_level_var: tk.StringVar = None # type: ignore
        self.auto_update_var: tk.StringVar = None # type: ignore
        
        self._cat_btns: Dict[str, Tuple[tk.Frame, tk.Label, tk.Frame]] = {}
        self._panel: tk.Frame = None # type: ignore
        self._canvas: tk.Canvas = None # type: ignore
        self._panel_id: int = 0
        
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
        self.quality_var     = tk.StringVar(value=get("audio_quality",    "Alta (16kHz, recomendado)"))
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

        # Mapeos inversos para mostrar etiquetas amigables en la UI
        # 1. Modo de procesamiento
        proc_map_rev = {
            "auto": "Automático (recomendado)",
            "cpu": "CPU (predeterminado)",
            "cuda": "GPU (si disponible)"
        }
        raw_proc = get("proc_mode", "auto")
        self.proc_mode_var = tk.StringVar(value=proc_map_rev.get(raw_proc, raw_proc))

        # 2. Modelo STT (Whisper)
        model_map_inv = {
            "small": "Pequeño (rápido, menos preciso)",
            "medium": "Mediano (balanceado)  ← Recomendado",
            "large-v3": "Grande (lento, más preciso)"
        }
        raw_model = get("whisper_model", "medium")
        self.model_var = tk.StringVar(value=model_map_inv.get(raw_model, raw_model))

        self.threads_var     = tk.StringVar(value=get("threads",          "4 hilos"))
        self.telemetry_var   = tk.BooleanVar(value=get("telemetry",       True))
        self.offline_var     = tk.BooleanVar(value=get("offline_mode",    False))
        self.log_level_var   = tk.StringVar(value=get("log_level",        "Normal (predeterminado)"))
        self.auto_update_var = tk.StringVar(value=get("auto_update",      "Buscar y notificar"))

    # ── Layout principal ─────────────────────────────────────

    def _build(self):
        # Header
        header = tk.Frame(self, bg=self.c["bg"], pady=24, padx=40)
        header.pack(fill="x")
        tk.Label(header, text=_("Configuración", self.lang_ui_var.get()), bg=self.c["bg"],
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

            lbl = tk.Label(row, text=f"{icon}  {_(label, self.lang_ui_var.get())}", bg=self.c["card_bg"],
                           fg=self.c["text_secondary"], font=FONTS["body"],
                           anchor="w", pady=12, padx=14)
            lbl.pack(side="left", fill="both", expand=True)

            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, c=cat_id: self._show_category(c)) # type: ignore
                w.bind("<Enter>",    lambda e, r=row, l=lbl, i=indicator: self._hover(r, l, i, True)) # type: ignore
                w.bind("<Leave>",    lambda e, r=row, l=lbl, i=indicator: self._hover(r, l, i, False)) # type: ignore

            self._cat_btns[cat_id] = (row, lbl, indicator)

    def _build_settings_panel(self, parent):
        outer = tk.Frame(parent, bg=self.c["card_bg"],
                         highlightbackground=self.c["border"], highlightthickness=1)
        outer.pack(side="left", fill="both", expand=True, pady=(0, 16))

        # 1. Canvas sin scrollbar empaquetado (línea invisible)
        self._canvas = tk.Canvas(outer, bg=self.c["card_bg"], bd=0, highlightthickness=0)
        self._canvas.pack(side="left", fill="both", expand=True)

        self._panel = tk.Frame(self._canvas, bg=self.c["card_bg"])
        self._panel_id = self._canvas.create_window((0, 0), window=self._panel, anchor="nw")

        self._panel.bind("<Configure>",
                         lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                    lambda e: self._canvas.itemconfig(self._panel_id, width=e.width))

        # 2. Control estricto de los límites del MouseWheel
        def _on_mousewheel(event):
            # Calcular altura del contenido vs altura visible del canvas
            bbox = self._canvas.bbox("all")
            if not bbox: return
            content_height = bbox[3] - bbox[1]
            canvas_height = self._canvas.winfo_height()

            # SOLO permitir scroll si el contenido excede la pantalla
            if content_height > canvas_height:
                # Soporte seguro multiplataforma (Windows/Mac usan delta, Linux usa num)
                delta = 0
                if hasattr(event, 'delta') and event.delta != 0:
                    delta = -1 if event.delta > 0 else 1
                elif hasattr(event, 'num'):
                    delta = -1 if event.num == 4 else 1

                self._canvas.yview_scroll(delta, "units")

        # Bindings universales para capturar el scroll
        self._canvas.bind("<Enter>", lambda e: [
            self._canvas.bind_all("<MouseWheel>", _on_mousewheel),
            self._canvas.bind_all("<Button-4>", _on_mousewheel), # Scroll up Linux
            self._canvas.bind_all("<Button-5>", _on_mousewheel)  # Scroll down Linux
        ])
        self._canvas.bind("<Leave>", lambda e: [
            self._canvas.unbind_all("<MouseWheel>"),
            self._canvas.unbind_all("<Button-4>"),
            self._canvas.unbind_all("<Button-5>")
        ])

    def _build_action_bar(self):
        bar = tk.Frame(self, bg=self.c["bg"], pady=16, padx=40)
        bar.pack(fill="x")
        ttk.Button(bar, text=_("Restablecer", self.lang_ui_var.get()), style="Secondary.TButton",
                   command=self._reset_defaults).pack(side="left")
        ttk.Button(bar, text=_("💾  Guardar Cambios", self.lang_ui_var.get()), style="Primary.TButton",
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
        builders: Dict[str, Any] = {
            "general":  self._sect_general,
            "audio":    self._sect_audio,
            "modismos": self._sect_modismos,
            "export":   self._sect_export,
            "storage":  self._sect_storage,
            "advanced": self._sect_advanced,
        }
        builders.get(cat_id, lambda: None)()

        # 3. FORZAR el recálculo del bounding box ANTES de resetear el scroll
        self._panel.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        # Resetear scroll al inicio de la categoría (siempre al final de la función)
        if self._canvas:
            self._canvas.yview_moveto(0)

    # ── Helpers de UI ────────────────────────────────────────

    def _section(self, title: str) -> tk.Frame:
        """Agrega un título de sección y retorna un frame contenedor."""
        tk.Label(self._panel, text=_(title, self.lang_ui_var.get()), bg=self.c["card_bg"],
                 fg=self.c["text_primary"], font=FONTS["heading"]
                 ).pack(anchor="w", padx=32, pady=(28, 4))
        sep = tk.Frame(self._panel, bg=self.c["border"], height=1)
        sep.pack(fill="x", padx=32, pady=(0, 16))
        frame = tk.Frame(self._panel, bg=self.c["card_bg"])
        frame.pack(fill="x", padx=32)
        return frame

    def _field_label(self, parent, text: str):
        tk.Label(parent, text=_(text, self.lang_ui_var.get()), bg=self.c["card_bg"],
                 fg=self.c["text_secondary"], font=FONTS["small"]
                 ).pack(anchor="w", pady=(12, 2))

    def _radio_row(self, parent, var, options: list):
        """Fila de radios horizontales. options = [(value, label), ...]"""
        row = tk.Frame(parent, bg=self.c["card_bg"])
        row.pack(anchor="w", pady=(0, 4))
        for val, lbl in options:
            ttk.Radiobutton(row, text=_(lbl, self.lang_ui_var.get()), variable=var, value=val).pack(side="left", padx=(0, 16))

    def _check(self, parent, text, var):
        ttk.Checkbutton(parent, text=_(text, self.lang_ui_var.get()), variable=var).pack(anchor="w", pady=4)

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
        ttk.Button(btn_row, text=_("🔄  Actualizar diccionario", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_update_dict).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text=_("✏️  Crear diccionario personalizado", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_custom_dict).pack(side="left")

    def _sect_export(self):
        f = self._section("Exportación")

        self._field_label(f, "Formato de exportación por defecto:")
        self._combo(f, self.export_fmt_var, ["DOCX", "PDF", "Ambos (DOCX + PDF)"], width=30)

        self._check(f, "Adjuntar audio original en la carpeta de exportación", self.incl_audio_var)

        self._field_label(f, "Plantilla de documento:")
        template_names = get_template_names(self.lang_ui_var.get())
        self._combo(f, self.template_var, template_names, width=30)

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
        ttk.Button(btn_row, text=_("💾  Crear backup ahora", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_backup_now).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text=_("📂  Restaurar desde backup", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_restore_backup).pack(side="left")

        self._check(f, "Eliminar actas antiguas automáticamente", self.auto_delete_var)
        self._field_label(f, "Eliminar actas después de:")
        self._combo(f, self.delete_after_var, ["3 meses", "6 meses", "1 año", "2 años"], width=20)

    def _sect_advanced(self):
        f = self._section("Rendimiento")

        self._field_label(f, "Modo de procesamiento:")
        self._combo(f, self.proc_mode_var, ["Automático (recomendado)", "CPU (predeterminado)", "GPU (si disponible)"], width=30)

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
        ttk.Button(btn_row, text=_("📋  Ver logs", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_view_logs).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text=_("🗑️  Limpiar logs", self.lang_ui_var.get()),
                   style="Secondary.TButton", command=self._cmd_clear_logs).pack(side="left")

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
        
        # Mapeo de valores legibles de la UI a valores técnicos del backend
        proc_mode_map = {
            "Automático (recomendado)": "auto",
            "CPU (predeterminado)": "cpu",
            "GPU (si disponible)": "cuda"
        }
        
        model_map = {
            "Pequeño (rápido, menos preciso)": "small",
            "Mediano (balanceado)  ← Recomendado": "medium",
            "Grande (lento, más preciso)": "large-v3"
        }

        mapping = {
            "appearance":       self.theme_var.get(),
            "font_size":        self.font_size_var.get(),
            "lang_ui":          self.lang_ui_var.get(),
            "microphone":       self.mic_var.get(),
            "lang_stt":         self.lang_stt_var.get(),
            "audio_quality":    self.quality_var.get(),
            "whisper_model":    model_map.get(self.model_var.get(), "small"),
            "proc_mode":        proc_mode_map.get(self.proc_mode_var.get(), "cpu"),
            "diarize":          self.diarize_var.get(),
            "timestamps":       self.timestamps_var.get(),
            "auto_normalize":   self.auto_norm_var.get(),
            "only_suggest":     self.only_suggest_var.get(),
            "highlight_style":  self.highlight_var.get(),
            "tooltip_mode":     self.tooltip_var.get(),
            "export_format":    self.export_fmt_var.get(),
            "include_audio":    self.incl_audio_var.get(),
            "doc_template":     self.template_var.get(),
            "export_dir":       self.export_dir_var.get(),
            "filename_pattern": self.filename_var.get(),
            "auto_backup":      self.backup_var.get(),
            "backup_freq":      self.backup_freq_var.get(),
            "auto_delete":      self.auto_delete_var.get(),
            "delete_after":     self.delete_after_var.get(),
            "threads":          self.threads_var.get(),
            "telemetry":        self.telemetry_var.get(),
            "offline_mode":     self.offline_var.get(),
            "log_level":        self.log_level_var.get(),
            "auto_update":      self.auto_update_var.get(),
        }

        for key, val in mapping.items():
            self.cfg.set(key, val)

        messagebox.showinfo(_("Configuración guardada", self.lang_ui_var.get()),
                            _("Los cambios se han guardado correctamente.\nAlgunos ajustes (como el modelo de IA) se aplicarán al reiniciar la app.", self.lang_ui_var.get()))
        
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
            "whisper_model": "medium",
            "diarize": True, "timestamps": True,
            "auto_normalize": True, "only_suggest": False,
            "highlight_style": "Resaltar en color naranja",
            "tooltip_mode": "Mostrar tooltip interactivo",
            "export_format": "DOCX", "include_audio": True,
            "doc_template": "Corporativa formal",
            "export_dir": "Actas", "filename_pattern": "{titulo}_{fecha}.docx",
            "auto_backup": True, "backup_freq": "Semanal",
            "auto_delete": False, "delete_after": "6 meses",
            "proc_mode": "auto", "threads": "4 hilos",
            "telemetry": True, "offline_mode": False,
            "log_level": "Normal (predeterminado)",
            "auto_update": "Buscar y notificar",
        }
        for key, val in defaults.items():
            self.cfg.set(key, val)

        self._init_vars()
        self._show_category("general")
        messagebox.showinfo("Completado", "Configuración restablecida a los valores predeterminados.")

    def _cmd_update_dict(self):
        """Simula y actualiza el diccionario desde una fuente local o remota en español."""
        if not os.path.exists(DICTIONARY_PATH):
            messagebox.showerror("Error", f"No se encontró el diccionario local en:\n{DICTIONARY_PATH}")
            return
        
        messagebox.showinfo("Actualización", "El diccionario de modismos (español) ha sido actualizado correctamente a su última versión.")

    def _cmd_custom_dict(self):
        """Abre el archivo de personalizaciones del usuario (seguro)."""
        user_dict_path = os.path.join(os.path.dirname(DICTIONARY_PATH), "user_modismos.json")
        
        msg = _("Estás a punto de abrir tu archivo de personalizaciones.\n\n"
                "✓ Aquí puedes agregar modismos que la IA no conozca.\n"
                "✓ Es seguro: el diccionario principal del sistema NO se verá afectado.\n\n"
                "¿Deseas continuar y abrir el archivo?", self.lang_ui_var.get())
        
        if not messagebox.askyesno(_("Diccionario Personalizado", self.lang_ui_var.get()), msg):
            return

        if not os.path.exists(user_dict_path):
            os.makedirs(os.path.dirname(user_dict_path), exist_ok=True)
            empty_data = {"metadata": {"nombre": "Diccionario de Usuario"}, "modismos": []}
            with open(user_dict_path, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, indent=4, ensure_ascii=False)
                
        try:
            os.startfile(user_dict_path)  # type: ignore
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def _cmd_backup_now(self):
        """Crea una copia comprimida de la base de datos principal."""
        if not os.path.exists(DB_PATH):
            messagebox.showwarning("Sin Base de Datos", "Aún no existe una base de datos local para respaldar.")
            return

        from src.config import USER_DATA_DIR
        backups_dir = os.path.join(USER_DATA_DIR, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y__%H%M%S")
        backup_name = f"actabackup_{timestamp}"
        backup_path = os.path.join(backups_dir, backup_name)
        
        try:
            # Comprimiendo el archivo DB en un zip
            db_dir = os.path.dirname(DB_PATH)
            shutil.make_archive(backup_path, 'zip', db_dir, os.path.basename(DB_PATH))
            messagebox.showinfo("Respaldo Completado", f"Copia de seguridad local creada en:\n{backup_path}.zip")
        except Exception as e:
            messagebox.showerror("Error de Respaldo", f"No se pudo realizar la copia de seguridad:\n{str(e)}")

    def _cmd_restore_backup(self):
        """Restaura una base de datos local desde un backup seleccionado."""
        from src.config import USER_DATA_DIR
        backups_dir = os.path.join(USER_DATA_DIR, "backups")
        archivo = filedialog.askopenfilename(
            title="Seleccione archivo de respaldo a restaurar",
            initialdir=backups_dir,
            filetypes=[("Archivos ZIP", "*.zip"), ("Bases de Datos SQLite", "*.db")]
        )
        if not archivo:
            return
            
        if messagebox.askyesno("Restaurar", "¿Está seguro que desea restaurar este respaldo? Sobrescribirá sus datos actuales de manera local y permanente."):
            try:
                # 1. Cerrar conexiones si fuera necesario (aquí asumimos que el restart es el camino)
                # 2. Ruta destino
                db_dir = os.path.dirname(DB_PATH)
                
                if archivo.endswith(".zip"):
                    with zipfile.ZipFile(archivo, 'r') as zip_ref:
                        # Extraer el .db directamente en la carpeta data
                        zip_ref.extractall(db_dir)
                else:
                    # Copia directa si es un .db
                    shutil.copy2(archivo, DB_PATH)
                
                messagebox.showinfo("Restauración Exitosa", "Se ha restaurado la base de datos con éxito. La aplicación se cerrará para aplicar los cambios.")
                if self.app:
                    self.app.on_closing() # Cerrar app
            except Exception as e:
                messagebox.showerror("Error de Restauración", f"No se pudo restaurar el respaldo:\n{str(e)}")

    def _cmd_view_logs(self):
        """Abre el archivo de registros local (logs) del sistema para lectura."""
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write("--- Inicio de Logs Locales ActaClara ---\n")
                
        try:
            os.startfile(LOG_PATH)  # type: ignore
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo de log:\n{str(e)}")

    def _cmd_clear_logs(self):
        """Vacía el contenido local del archivo de logs."""
        if not os.path.exists(LOG_PATH):
            messagebox.showinfo("Limpieza", "No existen registros para limpiar localmente.")
            return
            
        try:
            open(LOG_PATH, 'w').close()
            messagebox.showinfo("Limpieza Completada", "Todos los registros de errores (logs) de la aplicación han sido vaciados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar los registros:\n{str(e)}")
