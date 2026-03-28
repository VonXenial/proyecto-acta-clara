"""
Vista Exportación - ActaClara
Estructura idéntica al mockup React: columna formulario + preview documento + panel inferior
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from src.ui.styles import COLORS, FONTS  # type: ignore
from src.utils.i18n import translate as _  # type: ignore
from src.database.db_manager import DBManager # type: ignore
from src.services.exporter import DocxExporter, PdfExporter, ActaMetadata # type: ignore
from src.models.acta import Acta # type: ignore
from src.utils.doc_templates.templates import get_template_names, get_template_key_by_name, get_template # type: ignore

# Clases de apoyo para Placeholders
class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#999999"
        self.default_fg_color = kwargs.get("foreground", "#000000")
        
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg_color)

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
            
    def get_real_value(self):
        val = self.get()
        return "" if val == self.placeholder else val

class PlaceholderText(tk.Text):
    def __init__(self, container, placeholder, theme_colors, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.c = theme_colors
        self.placeholder_color = "#999999"
        self.default_fg_color = self.c["text_primary"]
        
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        if self.get("1.0", tk.END).strip() == self.placeholder:
            self.delete("1.0", tk.END)
            self.configure(fg=self.default_fg_color)

    def _add_placeholder(self, e=None):
        if not self.get("1.0", tk.END).strip():
            self.insert("1.0", self.placeholder)
            self.configure(fg=self.placeholder_color)
            
    def get_real_value(self):
        val = self.get("1.0", tk.END).strip()
        return "" if val == self.placeholder else val

class ExportView(tk.Frame):
    VIEW_NAME = "export"

    def __init__(self, parent, theme="light", lang="Español", app=None, db_manager=None, config_manager=None, normalizer=None):
        self.c    = COLORS[theme]
        self.lang = lang
        self.theme = theme
        self.app  = app
        self.db: DBManager = db_manager # type: ignore
        self.config = config_manager
        self.normalizer = normalizer
        self._acta: Acta = None # type: ignore
        super().__init__(parent, bg=self.c["bg"])
        self.participantes_txt: tk.Text = None # type: ignore
        self.doc_canvas: tk.Canvas = None # type: ignore
        self.doc_frame: tk.Frame = None # type: ignore
        self.form_container: tk.Frame = None # type: ignore
        
        # Diccionario para guardar referencias a campos dinámicos
        self._dynamic_fields: Dict[str, Any] = {}
        self._section_text_areas: Dict[str, tk.Text] = {}

        # ── Variables de formulario ───────────────────────────
        self._titulo_var     = tk.StringVar()
        self._fecha_var      = tk.StringVar()
        self._objetivo_var   = tk.StringVar()
        self._ruta_var       = tk.StringVar()
        self._doc_title_var  = tk.StringVar() # Título personalizado del documento final

        # Variables checkboxes secciones
        self._cb_acuerdos    = tk.BooleanVar(value=False)
        self._cb_tareas      = tk.BooleanVar(value=False)
        self._cb_compromisos = tk.BooleanVar(value=False)
        self._cb_notas       = tk.BooleanVar(value=False)

        # Variables radios
        self._fmt_doc        = tk.StringVar(value="ambos")   # docx | pdf | ambos
        self._fmt_audio      = tk.StringVar(value="mp3")     # wav  | mp3 | ninguno
        self._guardar_local  = tk.BooleanVar(value=True)

        self._build()

    def set_context(self, context):
        if "acta_id" in context and self.db:
            acta = self.db.get_acta_by_id(context["acta_id"])
            if acta:
                self._acta = acta
                self._titulo_var.set(acta.titulo)
                if acta.fecha_creacion:
                    self._fecha_var.set(acta.fecha_creacion.strftime("%d-%m-%Y %H:%M"))
                else:
                    self._fecha_var.set(datetime.now().strftime("%d-%m-%Y %H:%M"))
                
                if self.config:
                    # Carpeta por defecto en la raíz del proyecto llamada 'Actas'
                    default_dir = self.config.get("export_dir", "Actas")
                    if not default_dir: default_dir = "Actas"
                    self._ruta_var.set(default_dir)
                    
                    fmt_conf = self.config.get("export_fmt", "Ambos (DOCX + PDF)").lower()
                    if "ambos" in fmt_conf:
                        self._fmt_doc.set("ambos")
                    elif "pdf" in fmt_conf:
                        self._fmt_doc.set("pdf")
                    else:
                        self._fmt_doc.set("docx")
                    
                    # Sincronizar audio
                    incl_audio = self.config.get("include_audio", True)
                    if not incl_audio:
                        self._fmt_audio.set("none")
                    else:
                        self._fmt_audio.set("mp3") # Por defecto MP3 si está habilitado
                
                # Reiniciar checkboxes de secciones opcionales por defecto (desactivadas)
                self._cb_acuerdos.set(False)
                self._cb_tareas.set(False)
                self._cb_compromisos.set(False)
                self._cb_notas.set(False)
                
                # Título por defecto según plantilla
                tpl_name = self.config.get("doc_template", "Corporativa formal")
                self._doc_title_var.set(_(tpl_name, self.lang))
                
                # Forzar rebuild del formulario para reflejar la plantilla de config
                self._rebuild_dynamic_form()
                self._refresh_preview()
                
                # Mostrar botón omitir
                if hasattr(self, "omitir_btn"):
                    self.omitir_btn.pack(side="top", fill="x", pady=(0, 10))

    def _clear_fields(self):
        """Limpia los datos del acta actual y resetea el formulario."""
        if not self._acta:
            return
            
        if not messagebox.askyesno(_("Confirmar", self.lang), _("¿Estás seguro de que quieres cancelar y limpiar el formulario? Se perderán los cambios no guardados.", self.lang)):
            return
            
        self._acta = None # type: ignore
        self._titulo_var.set("")
        self._fecha_var.set("")
        self._objetivo_var.set("")
        self._doc_title_var.set("")
        
        # Reset checkboxes
        self._cb_acuerdos.set(False)
        self._cb_tareas.set(False)
        self._cb_compromisos.set(False)
        self._cb_notas.set(False)
        
        # Rebuild para limpiar campos dinámicos
        self._rebuild_dynamic_form()
        
        # Limpiar áreas de texto de secciones si existen
        for txt in self._section_text_areas.values():
            txt.delete("1.0", tk.END)
            txt.pack_forget()
            
        # Ocultar botón omitir
        if hasattr(self, "omitir_btn"):
            self.omitir_btn.pack_forget()
            
        self._refresh_preview()
        
        # Feedback en la barra de navegación o similar si existiera
        # Volver al historial si es preferible, o dejar en blanco
        # self.app.show_view("history") # Opcional

    # ═══════════════════════════════════════════════════════════
    # BUILD PRINCIPAL
    # ═══════════════════════════════════════════════════════════

    def _build(self):
        """Layout: área principal (2 columnas) + panel inferior fijo."""
        # Área principal ocupa todo el espacio disponible
        self._build_main_area()
        # Panel inferior fijo de ~110px
        self._build_bottom_panel()

    # ───────────────────────────────────────────────────────────
    # ÁREA PRINCIPAL: dos columnas con PanedWindow
    # ───────────────────────────────────────────────────────────

    def _build_main_area(self):
        """Divide el área en columna izquierda (form) y derecha (preview)."""
        paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=0,           # Sin handle visible
            sashrelief="flat",
            bg=self.c["border"],
        )
        paned.pack(fill="both", expand=True)

        # ── Columna izquierda: 40% ────────────────────────────
        left = tk.Frame(paned, bg=self.c["bg"])
        paned.add(left, minsize=340, width=480)

        # ── Columna derecha: 60% ─────────────────────────────
        right = tk.Frame(paned, bg="#E5E5E5")
        paned.add(right, minsize=400)

        self._build_form_column(left)
        self._build_preview_column(right)

    # ═══════════════════════════════════════════════════════════
    # COLUMNA IZQUIERDA — Formulario
    # ═══════════════════════════════════════════════════════════

    def _build_form_column(self, parent):
        """
        Formulario con scroll: título, fecha, participantes,
        objetivo y checkboxes de secciones.
        """
        # Canvas + Scrollbar para scroll vertical
        canvas = tk.Canvas(parent, bg=self.c["bg"], highlightthickness=0)
        sb     = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.c["bg"], padx=32, pady=24)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Header: ← + Título ───────────────────────────────
        hdr = tk.Frame(inner, bg=self.c["bg"])
        hdr.pack(fill="x", pady=(0, 20))

        back_lbl = tk.Label(
            hdr,
            text="←",
            bg=self.c["bg"],
            fg=self.c["text_secondary"],
            font=FONTS["heading"],
            cursor="hand2",
            padx=4,
        )
        back_lbl.pack(side="left")
        back_lbl.bind("<Button-1>", lambda e: self.app.show_view("history") if self.app else None)

        tk.Label(
            hdr,
            text=_("Estructura del Acta", self.lang),
            bg=self.c["bg"],
            fg=self.c["text_primary"],
            font=FONTS["title"],
        ).pack(side="left", padx=10)

        # ── Formulario Dinámico ─────────────────────────────
        self.form_container = tk.Frame(inner, bg=self.c["bg"])
        self.form_container.pack(fill="x")
        
        self._rebuild_dynamic_form()

        # ── Card de checkboxes ────────────────────────────────
        tk.Label(
            inner,
            text=_("Secciones del acta", self.lang),
            bg=self.c["bg"],
            fg=self.c["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(8, 8))

        cb_card = tk.Frame(
            inner,
            bg=self.c["card_bg"],
            padx=16,
            pady=14,
            highlightbackground=self.c["border"],
            highlightthickness=1,
        )
        cb_card.pack(fill="x", pady=(0, 16))

        sections = [
            ("acuerdos",    self._cb_acuerdos,    _("Acuerdos alcanzados", self.lang)),
            ("tareas",      self._cb_tareas,      _("Tareas asignadas y responsables", self.lang)),
            ("compromisos", self._cb_compromisos, _("Compromisos pendientes", self.lang)),
            ("notas",       self._cb_notas,       _("Notas adicionales", self.lang)),
        ]
        
        for k, v, label in sections:
            # FRAME POR SECCIÓN: Contiene el checkbox y su editor para mantener el orden
            sect_f = tk.Frame(cb_card, bg=self.c["card_bg"])
            sect_f.pack(fill="x", pady=4)
            
            # Definir un callback cerrado para evitar problemas de referencia en lambdas
            def toggle_cmd(key_val=k, var_val=v):
                return self._toggle_section_editor(key_val, var_val)
            
            cb = ttk.Checkbutton(
                sect_f,
                text=label,
                variable=v,
                style="TCheckbutton",
                command=toggle_cmd
            )
            cb.pack(anchor="w")
            
            # Editor de texto que aparece al marcar (Hijo del sect_f)
            txt = tk.Text(
                sect_f,
                height=4,
                font=FONTS["small"],
                wrap="word",
                relief="solid",
                bd=1,
                padx=5,
                pady=5,
                bg=self.c["bg"],
                fg=self.c["text_primary"]
            )
            self._section_text_areas[k] = txt
            txt.bind("<KeyRelease>", self._refresh_preview)
            
            if v.get():
                txt.pack(fill="x", pady=(2, 8))
            else:
                txt.pack_forget()

    def _get_field_meta(self) -> dict:
        """Retorna el mapeo de campos internos a nombres legibles y placeholders estructurado."""
        return {
            "purpose": (_("Objetivo", self.lang), _("Ej: Definir objetivos de venta Q4", self.lang)),
            "date": (_("Fecha", self.lang), "DD-MM-YYYY"),
            "start_time": (_("Hora inicio", self.lang), "HH:MM"),
            "end_time": (_("Hora fin", self.lang), "HH:MM"),
            "location": (_("Lugar", self.lang), _("Ej: Sala de juntas 2 / Microsoft Teams", self.lang)),
            "attendees": (_("Participantes", self.lang), _("Ej: Juan P., Maria G...", self.lang)),
            "absentees": (_("Ausentes", self.lang), _("Ej: Carlos M.", self.lang)),
            "organization_name": (_("Organización", self.lang), _("Ej: Acme Corp", self.lang)),
            "project_name": (_("Proyecto", self.lang), _("Ej: Proyecto Omega", self.lang)),
            "meeting_title": (_("Título de la reunión", self.lang), _("Ej: Revisión Semanal", self.lang)),
            "called_by": (_("Convocado por", self.lang), _("Ej: Dirección Ejecutiva", self.lang)),
            "secretary": (_("Secretario", self.lang), _("Ej: Pedro Pérez", self.lang)),
            "agenda_items": (_("Puntos de agenda", self.lang), _("Detalle de temas a tratar...", self.lang)),
            "additional_notes": (_("Notas adicionales", self.lang), _("Notas generales...", self.lang)),
            "next_meeting_date": (_("Fecha próxima reunión", self.lang), "DD-MM-YYYY"),
            "next_meeting_time": (_("Hora próxima reunión", self.lang), "HH:MM"),
            "next_meeting_location": (_("Lugar próxima reunión", self.lang), _("Sala / Enlace", self.lang)),
            "financial_report": (_("Reporte financiero", self.lang), _("Resumen financiero...", self.lang)),
            "committee_reports": (_("Reportes de comité", self.lang), _("Resumen de reportes...", self.lang)),
            "old_business": (_("Temas pasados", self.lang), _("Seguimiento de temas previos...", self.lang)),
            "new_business": (_("Temas nuevos", self.lang), _("Discusión de nuevos temas...", self.lang)),
            "adjournment_time": (_("Hora de cierre", self.lang), "HH:MM"),
            "participants": (_("Participantes", self.lang), _("Nombres...", self.lang)),
            "project_status_update": (_("Actualización de estado", self.lang), _("Estado general...", self.lang)),
            "issues_challenges": (_("Problemas / Desafíos", self.lang), _("Obstáculos...", self.lang)),
            "action_items": (_("Elementos de acción", self.lang), _("Responsabilidades...", self.lang)),
            "next_steps": (_("Próximos pasos", self.lang), _("Acciones futuras...", self.lang)),
            "chairperson": (_("Presidente / Moderador", self.lang), _("Nombre...", self.lang)),
            "year_summary": (_("Resumen del año", self.lang), _("Balance general...", self.lang)),
            "strategic_plan": (_("Plan estratégico", self.lang), _("Estrategia a futuro...", self.lang)),
            "client_name": (_("Nombre del cliente", self.lang), _("Ej: Empresa XYZ", self.lang)),
            "objectives": (_("Objetivos", self.lang), _("Propósito...", self.lang)),
            "client_feedback": (_("Retroalimentación del cliente", self.lang), _("Comentarios...", self.lang)),
            "key_decisions": (_("Decisiones clave", self.lang), _("Definiciones...", self.lang)),
            "financial_performance_review": (_("Revisión financiera", self.lang), _("Rendimiento...", self.lang)),
            "budget_discussion": (_("Discusión de presupuesto", self.lang), _("Análisis...", self.lang)),
            "financial_strategy": (_("Estrategia financiera", self.lang), _("Planeación...", self.lang)),
            "decisions": (_("Decisiones", self.lang), _("Lo acordado...", self.lang))
        }

    def _rebuild_dynamic_form(self):
        """Construye los campos basados en la plantilla actual."""
        for widget in self.form_container.winfo_children():
            widget.destroy()
        
        self._dynamic_fields = {}
        
        # --- CAMPO TÍTULO PERSONALIZADO (AL TOP) ---
        lbl_t = tk.Label(self.form_container, text=_("Título del Documento", self.lang), 
                        bg=self.c["bg"], fg=self.c["text_secondary"], font=FONTS["small"])
        lbl_t.pack(anchor="w", pady=(0, 2))
        ent_t = ttk.Entry(self.form_container, textvariable=self._doc_title_var, font=FONTS["body"])
        ent_t.pack(fill="x", pady=(0, 15))
        ent_t.bind("<KeyRelease>", self._refresh_preview)
        # -------------------------------------------
        
        # Obtener plantilla de configuración
        tpl_name = "Corporativa formal"
        if self.config:
            tpl_name = self.config.get("doc_template", "Corporativa formal")
        
        tpl_key = get_template_key_by_name(tpl_name, self.lang)
        tpl_data = get_template(tpl_key)
        
        field_meta = self._get_field_meta()
        
        for field in tpl_data["fields"]:
            label_text, placeholder = field_meta.get(field, (field.replace("_", " ").title(), ""))
            
            # Decidir si es Entry o Text
            if field in ["attendees", "participants", "agenda_items", "financial_report", "strategic_plan"]:
                # Text area
                lbl = tk.Label(self.form_container, text=label_text, bg=self.c["bg"], 
                              fg=self.c["text_secondary"], font=FONTS["small"])
                lbl.pack(anchor="w", pady=(10, 2))
                
                txt = PlaceholderText(self.form_container, placeholder, self.c, height=3, font=FONTS["body"],
                                    relief="solid", bd=1, bg=self.c["bg"], fg=self.c["text_primary"])
                txt.pack(fill="x", pady=(0, 5))
                txt.bind("<KeyRelease>", self._refresh_preview)
                self._dynamic_fields[field] = txt
            else:
                # Entry
                lbl = tk.Label(self.form_container, text=label_text, bg=self.c["bg"], 
                              fg=self.c["text_secondary"], font=FONTS["small"])
                lbl.pack(anchor="w", pady=(10, 2))
                
                ent = PlaceholderEntry(self.form_container, placeholder, font=FONTS["body"], 
                                      foreground=self.c["text_primary"])
                ent.pack(fill="x", pady=(0, 5))
                ent.bind("<KeyRelease>", self._refresh_preview)
                self._dynamic_fields[field] = ent

    def _toggle_section_editor(self, key: str, var: tk.BooleanVar):
        txt = self._section_text_areas.get(key)
        if not txt: return
        
        if var.get():
            txt.pack(fill="x", pady=(2, 8))
        else:
            txt.pack_forget()
        self._refresh_preview()

    def _form_field(self, parent, label_text: str, widget: tk.Widget):
        """Helper: label + widget con separación estándar (legacy)."""
        pass


    # ═══════════════════════════════════════════════════════════
    # COLUMNA DERECHA — Preview del documento
    # ═══════════════════════════════════════════════════════════

    def _build_preview_column(self, parent):
        """
        Panel gris con badge 'Listo para exportar' y documento
        blanco simulado con secciones del acta.
        """
        # Centramos el documento dentro del panel
        center = tk.Frame(parent, bg="#E5E5E5")
        center.pack(fill="both", expand=True, padx=32, pady=32)

        # Canvas con scrollbar para el documento
        doc_canvas = tk.Canvas(center, bg="#E5E5E5", highlightthickness=0)
        doc_sb     = ttk.Scrollbar(center, orient="vertical",
                                   command=doc_canvas.yview)
        doc_canvas.configure(yscrollcommand=doc_sb.set)

        doc_sb.pack(side="right", fill="y")
        doc_canvas.pack(side="left", fill="both", expand=True)

        # Frame blanco = "hoja de papel"
        doc = tk.Frame(doc_canvas, bg="white", padx=40, pady=36)
        doc_win = doc_canvas.create_window((0, 0), window=doc, anchor="nw")

        def _resize_doc(e):
            doc_canvas.itemconfig(doc_win, width=e.width)
        doc_canvas.bind("<Configure>", _resize_doc)
        doc.bind("<Configure>",
                 lambda e: doc_canvas.configure(
                     scrollregion=doc_canvas.bbox("all")))

        self.doc_canvas = doc_canvas
        self.doc_frame = doc
        
        self._refresh_preview()

    def _refresh_preview(self, *args):
        if not hasattr(self, "doc_frame"):
            return
        
        for w in self.doc_frame.winfo_children():
            w.destroy()
            
        self._build_document_content(self.doc_frame)
        self.doc_canvas.update_idletasks()
        self.doc_canvas.configure(scrollregion=self.doc_canvas.bbox("all"))

    def _build_document_content(self, parent):
        """Simula el contenido del acta en el documento blanco."""
        
        template_name = "Corporativa formal"
        if self.config:
            template_name = self.config.get("doc_template", "Corporativa formal")
        
        tpl_key = get_template_key_by_name(template_name, self.lang)
        tpl_data = get_template(tpl_key)
            
        font_base = "Segoe UI"
        primary_color = "#1F497D" # Corporate Blue
        sec_color = "#2E74B5"
        title_align = "center"

        field_meta = self._get_field_meta()

        def get_v(key):
            widget = self._dynamic_fields.get(key)
            if not widget: return ""
            if isinstance(widget, PlaceholderEntry): return widget.get_real_value()
            if isinstance(widget, PlaceholderText): return widget.get_real_value()
            return ""

        def get_lbl(key):
            return field_meta.get(key, (key.replace("_", " ").title(), ""))[0]

        def get_val_safe(key, fallback="(Sin información)"):
            v = get_v(key)
            return v if v else _(fallback, self.lang)

        # ── Encabezado del documento ─────────────────────────
        hdr = tk.Frame(parent, bg="white")
        hdr.pack(fill="x", pady=(0, 8))

        left_hdr = tk.Frame(hdr, bg="white")
        left_hdr.pack(side="left" if title_align == "w" else "top", fill="x" if title_align == "center" else "none")

        main_title = self._doc_title_var.get() or get_v("meeting_title") or get_v("project_name") or template_name
        tk.Label(left_hdr,
                 text=main_title.upper(),
                 bg="white", fg=primary_color,
                 font=(font_base, 14, "bold")).pack(anchor=title_align)

        tk.Label(left_hdr,
                 text=_("CONFIDENCIAL", self.lang),
                 bg="white", fg="#6B7A8D",
                 font=(font_base, 9)).pack(anchor=title_align)

        right_hdr = tk.Frame(hdr, bg="white")
        if title_align == "w":
            right_hdr.pack(side="right")
        else:
            right_hdr.pack(side="top", anchor="e", pady=(4, 0))

        fecha_v = get_v("date") or datetime.now().strftime("%d-%m-%Y")
        tk.Label(right_hdr,
                 text=f"{_('Fecha', self.lang)}: {fecha_v}",
                 bg="white", fg=primary_color,
                 font=(font_base, 9),
                 justify="right").pack(anchor="e")

        ref_id = f"REF-{self._acta.id:04d}" if self._acta and self._acta.id else "REF-0000"
        tk.Label(right_hdr,
                 text=f"Ref: {ref_id}",
                 bg="white", fg=primary_color,
                 font=(font_base, 9),
                 justify="right").pack(anchor="e")

        # Separador grueso bajo el encabezado
        tk.Frame(parent, bg=primary_color, height=2).pack(fill="x", pady=(4, 16))

        # ── Secciones dinámicas ──────────────────────────
        sections_to_render: list[tuple[str, str, Any]] = []
        fields = tpl_data.get("fields", [])
        
        # 1. Agrupar Información General
        info_group_keys = ["meeting_title", "project_name", "organization_name", "client_name", 
                           "purpose", "objectives", "date", "start_time", "end_time", 
                           "location", "called_by", "chairperson", "secretary", "adjournment_time"]
        
        content_info = []
        for k in info_group_keys:
            if k in fields:
                content_info.append((get_lbl(k) + ":", get_val_safe(k)))
        
        if content_info:
            sections_to_render.append((_("Información General", self.lang), "grid", content_info))

        # 2. Participantes y Ausentes
        parts_keys = ["attendees", "participants"]
        for k in parts_keys:
            if k in fields:
                val = get_v(k)
                asist_str = "\n".join(f"- {p.strip()}" for p in val.split('\n') if p.strip()) if val else _("Sin participantes registrados.", self.lang)
                sections_to_render.append((get_lbl(k), "text", asist_str))
                
        if "absentees" in fields:
            val = get_v("absentees")
            aus_str = "\n".join(f"- {p.strip()}" for p in val.split('\n') if p.strip()) if val else _("Sin ausentes registrados.", self.lang)
            sections_to_render.append((get_lbl("absentees"), "text", aus_str))

        # 3. Transcripción Normalizada
        trans_title = _("Registro de Diálogo de la Sesión", self.lang)
        full_text = self._acta.transcripcion_texto if self._acta and self._acta.transcripcion_texto else ""
        
        # Normalizar si tenemos el servicio
        if self.normalizer and full_text:
            std_text, _mods = self.normalizer.normalize(full_text)
        else:
            std_text = full_text
            
        if not std_text:
            std_text = _("(Sin transcripción disponible)", self.lang)
            
        sections_to_render.append((trans_title, "text", std_text))

        # 4. Otras secciones dinámicas en el orden de la plantilla
        handled_keys = set(info_group_keys + parts_keys + ["absentees"])
        for field in fields:
            if field not in handled_keys:
                sections_to_render.append((get_lbl(field), "text", get_val_safe(field)))

        # 5. Secciones Opcionales de Checkbox
        for key, title in [("acuerdos", _("Acuerdos y Compromisos", self.lang)), 
                          ("tareas", _("Tareas y Responsables", self.lang)),
                          ("compromisos", _("Compromisos Pendientes", self.lang)),
                          ("notas", _("Notas Adicionales", self.lang))]:
            
            var = getattr(self, f"_cb_{key}", None)
            if var and var.get():
                txt_widget = self._section_text_areas.get(key)
                content = txt_widget.get("1.0", tk.END).strip() if txt_widget else ""
                if not content: content = _("(Sin contenido redactado)", self.lang)
                sections_to_render.append((title, "text", content))

        # Renderizar todas las secciones recolectadas
        for i, (title, s_type, s_content) in enumerate(sections_to_render, 1):
            self._doc_section(parent, f"{i}. {title}", primary_color, sec_color, font_base)
            
            if s_type == "text":
                tk.Label(parent, text=str(s_content), bg="white", fg=primary_color,
                         font=(font_base, 9), wraplength=480, justify="left").pack(anchor="w", pady=(4, 12))
            elif s_type == "grid":
                grid_f = tk.Frame(parent, bg="white")
                grid_f.pack(fill="x", pady=(4, 12))
                for k_lbl, v_val in s_content: # type: ignore
                    row = tk.Frame(grid_f, bg="white")
                    row.pack(fill="x", pady=2)
                    tk.Label(row, text=k_lbl, bg="white", fg=sec_color, width=17, anchor="w",
                             font=(font_base, 8, "bold")).pack(side="left")
                    tk.Label(row, text=str(v_val), bg="white", fg="#333333", anchor="w",
                             font=(font_base, 8)).pack(side="left", fill="x", expand=True)



    def _doc_section(self, parent, title: str, c_primary, c_sec, f_base):
        """Cabecera de sección dentro del documento (texto + línea)."""
        tk.Label(
            parent,
            text=title.upper(),
            bg="white", fg=c_sec,
            font=(f_base, 9, "bold"),
        ).pack(anchor="w", pady=(8, 2))
        tk.Frame(parent, bg="#E1E8F0", height=1).pack(fill="x", pady=(0, 4))

    # ═══════════════════════════════════════════════════════════
    # PANEL INFERIOR — Opciones de exportación
    # ═══════════════════════════════════════════════════════════

    def _build_bottom_panel(self):
        """
        Banda blanca fija (≈110px) con 4 zonas horizontales:
        Formato Doc | Audio | Ruta destino | Botón Exportar
        """
        # Borde superior
        tk.Frame(self, bg=self.c["border"], height=1).pack(fill="x")

        panel = tk.Frame(self, bg=self.c["card_bg"], height=110)
        panel.pack(fill="x")
        panel.pack_propagate(False)

        inner = tk.Frame(panel, bg=self.c["card_bg"], padx=24)
        inner.pack(fill="both", expand=True)

        # ── Col 1: Formato del documento ─────────────────────
        col1 = tk.Frame(inner, bg=self.c["card_bg"])
        col1.pack(side="left", fill="y", expand=True)

        tk.Label(col1,
                 text=_("Formato del documento", self.lang),
                 bg=self.c["card_bg"], fg=self.c["text_primary"],
                 font=FONTS["badge"]).pack(anchor="w", pady=(18, 6))

        radios_fmt = tk.Frame(col1, bg=self.c["card_bg"])
        radios_fmt.pack(anchor="w")
        for val, lbl in [("docx", "DOCX"), ("pdf", "PDF"), ("ambos", _("Ambos", self.lang))]:
            tk.Radiobutton(
                radios_fmt,
                text=lbl,
                variable=self._fmt_doc,
                value=val,
                bg=self.c["card_bg"],
                fg=self.c["text_primary"],
                activebackground=self.c["card_bg"],
                selectcolor=self.c["bg"],
                font=FONTS["body"],
            ).pack(side="left", padx=(0, 12))

        # Separador vertical
        tk.Frame(inner, bg=self.c["border"], width=1).pack(
            side="left", fill="y", padx=16, pady=16)

        # ── Col 2: Audio original ─────────────────────────────
        col2 = tk.Frame(inner, bg=self.c["card_bg"])
        col2.pack(side="left", fill="y", expand=True)

        tk.Label(col2,
                 text=_("Audio original", self.lang),
                 bg=self.c["card_bg"], fg=self.c["text_primary"],
                 font=FONTS["badge"]).pack(anchor="w", pady=(18, 6))

        radios_audio = tk.Frame(col2, bg=self.c["card_bg"])
        radios_audio.pack(anchor="w")
        for val, lbl in [("wav", "WAV"), ("mp3", "MP3"), ("none", _("Ninguno", self.lang))]:
            tk.Radiobutton(
                radios_audio,
                text=lbl,
                variable=self._fmt_audio,
                value=val,
                bg=self.c["card_bg"],
                fg=self.c["text_primary"],
                activebackground=self.c["card_bg"],
                selectcolor=self.c["bg"],
                font=FONTS["body"],
            ).pack(side="left", padx=(0, 12))

        # Separador vertical
        tk.Frame(inner, bg=self.c["border"], width=1).pack(
            side="left", fill="y", padx=16, pady=16)

        # ── Col 3: Ruta destino ───────────────────────────────
        col3 = tk.Frame(inner, bg=self.c["card_bg"])
        col3.pack(side="left", fill="y", expand=True)

        tk.Label(col3,
                 text=_("Carpeta de destino", self.lang),
                 bg=self.c["card_bg"], fg=self.c["text_primary"],
                 font=FONTS["badge"]).pack(anchor="w", pady=(18, 6))

        ruta_row = tk.Frame(col3, bg=self.c["card_bg"])
        ruta_row.pack(fill="x")

        ruta_entry = ttk.Entry(
            ruta_row,
            textvariable=self._ruta_var,
            font=FONTS["small"],
            state="readonly",
            width=28,
        )
        ruta_entry.pack(side="left", padx=(0, 6))

        ttk.Button(
            ruta_row,
            text="📁  " + _("Examinar", self.lang),
            style="Secondary.TButton",
            command=self._browse_folder,
        ).pack(side="left")

        ttk.Checkbutton(
            col3,
            text=_("Guardar en repositorio local", self.lang),
            variable=self._guardar_local,
        ).pack(anchor="w", pady=(6, 0))

        # Separador vertical
        tk.Frame(inner, bg=self.c["border"], width=1).pack(
            side="left", fill="y", padx=20, pady=16)

        # ── Col 4: Botón Exportar + Limpiar ────────────────────
        col4 = tk.Frame(inner, bg=self.c["card_bg"])
        col4.pack(side="left", fill="y", expand=True)

        # Espaciado vertical para centrar
        col4.pack_propagate(False)
        col4.configure(width=220) # Un poco más ancho para los dos botones

        buttons_inner = tk.Frame(col4, bg=self.c["card_bg"])
        buttons_inner.place(relx=0.5, rely=0.5, anchor="center")

        export_btn = ttk.Button(
            buttons_inner,
            text="📥  " + _("Exportar Acta", self.lang),
            style="Success.TButton",
            command=self._do_export,
        )
        export_btn.pack(side="top", fill="x", pady=(0, 5))

        self.omitir_btn = ttk.Button(
            buttons_inner,
            text="✕  " + _("Cancelar y Limpiar", self.lang),
            style="Secondary.TButton",
            command=self._clear_fields
        )
        # Se mostrará solo si hay acta vía set_context
        if not self._acta:
            self.omitir_btn.pack_forget()
        else:
            self.omitir_btn.pack(side="top", fill="x")

    # ═══════════════════════════════════════════════════════════
    # HANDLERS
    # ═══════════════════════════════════════════════════════════

    def _browse_folder(self):
        """Abre diálogo de selección de carpeta."""
        folder = filedialog.askdirectory(
            title=_("Seleccionar carpeta de destino", self.lang),
            initialdir=self._ruta_var.get(),
        )
        if folder:
            self._ruta_var.set(folder)

    def _do_export(self):
        """Ejecuta la exportación de documentos, audio y los empaqueta en ZIP."""
        if not self._acta:
            messagebox.showwarning(_("Advertencia", self.lang), _("Selecciona un acta desde el Historial primero.", self.lang))
            return
            
        titulo_limpio = self._doc_title_var.get().strip()
        if not titulo_limpio: titulo_limpio = self._acta.titulo or "Acta"
        
        # Limpiar caracteres prohibidos en nombres de archivo
        import re
        titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", titulo_limpio)
        
        # Generar nombre base usando el patrón de configuración
        pattern = "{titulo}"
        if self.config:
            pattern = self.config.get("filename_pattern", "{titulo}")
            # Quitar extensión del patrón si el usuario la puso (nosotros la añadimos luego)
            pattern = pattern.split('.')[0]
            
        fecha_str = datetime.now().strftime("%d-%m-%Y")
        base_name = pattern.replace("{titulo}", titulo_limpio).replace("{fecha}", fecha_str)
        
        formato_doc = self._fmt_doc.get().lower()
        formato_audio = self._fmt_audio.get().lower()
        
        # Validar ruta base (usar 'Actas' si está vacío)
        ruta_base_str = self._ruta_var.get().strip()
        if not ruta_base_str:
            ruta_base_str = "Actas"
            self._ruta_var.set(ruta_base_str)
            
        ruta_base = Path(ruta_base_str)
        
        if not ruta_base.exists():
            try:
                ruta_base.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror(_("Error", self.lang), f"No se pudo crear el directorio destino:\n{e}")
                return
        
        # 1. Construir ActaMetadata
        def get_v(key):
            widget = self._dynamic_fields.get(key)
            if not widget: return ""
            if isinstance(widget, PlaceholderEntry): return widget.get_real_value()
            if isinstance(widget, PlaceholderText): return widget.get_real_value()
            return ""

        parts_text = get_v("attendees") or get_v("participants") or ""
        parts = [p.strip() for p in parts_text.split('\n') if p.strip()]
        
        # Recopilar secciones opcionales con su contenido redactado
        secciones_manuales = {}
        for key in ["acuerdos", "tareas", "compromisos", "notas"]:
            if getattr(self, f"_cb_{key}").get():
                txt_widget = self._section_text_areas.get(key)
                content = txt_widget.get("1.0", tk.END).strip() if txt_widget else ""
                if content:
                    secciones_manuales[key] = content

        metadata = ActaMetadata(
            proyecto=get_v("project_name") or "ActaClara",
            objetivo=get_v("purpose") or get_v("objectives") or "",
            asistentes=parts,
            acuerdos=[secciones_manuales.get("acuerdos", "")],
            compromisos=[secciones_manuales.get("compromisos", "")] 
        )
        
        template_name = "Corporativa formal"
        if self.config:
            template_name = self.config.get("doc_template", "Corporativa formal")
        
        tpl_key = get_template_key_by_name(template_name)
        tpl_data = get_template(tpl_key)
        
        archivos_generados = []
        ruta_sin_ext = ruta_base / titulo_limpio
        
        # 2. Exportar Documentos
        try:
            if formato_doc in ["docx", "ambos"]:
                docx_path = ruta_base / f"{base_name}.docx"
                exporter = DocxExporter(self._acta, metadata, self.db, template_name)
                exporter.apply_template()
                self._add_exporter_sections(exporter, template_name)
                # Exportar y registrar
                out_path = exporter.save_and_record(self._acta.id, docx_path)
                archivos_generados.append(out_path)
                
            if formato_doc in ["pdf", "ambos"]:
                pdf_path = ruta_base / f"{base_name}.pdf"
                exporter = PdfExporter(self._acta, metadata, self.db, template_name)
                exporter.apply_template()
                self._add_exporter_sections(exporter, template_name)
                out_path = exporter.save_and_record(self._acta.id, pdf_path)
                archivos_generados.append(out_path)
        except Exception as e:
            messagebox.showerror(_("Error de exportación", self.lang), f"Falló la generación del documento:\n{e}")
            return
            
        # 3. Exportar Audio
        if formato_audio != "none" and self._acta.archivo_audio_ruta:
            audio_path = Path(self._acta.archivo_audio_ruta)
            if audio_path.exists():
                destino_audio = ruta_base / f"{base_name}.{formato_audio}"
                try:
                    # Intento de conversión
                    if audio_path.suffix.lower() != f".{formato_audio}":
                        from pydub import AudioSegment # type: ignore
                        aud = AudioSegment.from_file(str(audio_path))
                        aud.export(str(destino_audio), format=formato_audio)
                    else:
                        shutil.copy2(audio_path, destino_audio)
                    archivos_generados.append(destino_audio)
                except Exception as e:
                    # Si pydub/ffmpeg falla, copiar el original
                    fallback = ruta_base / f"{titulo_limpio}{audio_path.suffix}"
                    shutil.copy2(audio_path, fallback)
                    archivos_generados.append(fallback)
                    
        # 4. Crear ZIP si hay archivos
        if archivos_generados:
            zip_path = ruta_base / f"{base_name}.zip"
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for arch in archivos_generados:
                        zipf.write(arch, arcname=arch.name)
                        
                # Eliminar archivos intermedios si se creó el zip
                for arch in archivos_generados:
                    if arch.exists():
                        arch.unlink()
                
                # 5. Respaldar en repositorio local (Backups) si aplica
                msj_respaldo = ""
                if self._guardar_local.get():
                    try:
                        local_repo = Path("backups")
                        local_repo.mkdir(parents=True, exist_ok=True)
                        
                        # Evitar copia si el destino ya es la carpeta de backups
                        if ruta_base.resolve() != local_repo.resolve():
                            shutil.copy2(zip_path, local_repo / zip_path.name)
                            msj_respaldo = f"\n✅ {_('Copia de seguridad guardada en backups/', self.lang)}"
                        else:
                            msj_respaldo = f"\n✅ {_('Archivo guardado en el repositorio local.', self.lang)}"
                    except Exception as e:
                        msj_respaldo = f"\n⚠️ {_('No se pudo crear el respaldo local:', self.lang)} {e}"

                messagebox.showinfo(
                    _("Exportación completada", self.lang),
                    f"{_('Acta generada exitosamente en ZIP', self.lang)}:\n\n"
                    f"📄 {zip_path.name}\n"
                    f"📁 {ruta_base}" + msj_respaldo
                )
                
                # Volver a historial
                if self.app:
                    self.app.show_view("history")
                    
            except Exception as e:
                messagebox.showerror(_("Error", self.lang), f"Ocurrió un error al comprimir:\n{e}")
                
    def _add_exporter_sections(self, exporter, template_name):
        """Agrega lógicamente las secciones a Docx/PdfExporter basadas en la plantilla."""
        tpl_key = get_template_key_by_name(template_name, self.lang)
        tpl_data = get_template(tpl_key)
        fields = tpl_data.get("fields", [])
        
        def get_v(key):
            widget = self._dynamic_fields.get(key)
            if not widget: return ""
            if isinstance(widget, PlaceholderEntry): return widget.get_real_value()
            if isinstance(widget, PlaceholderText): return widget.get_real_value()
            return ""

        def get_val_safe(key, fallback="(Sin información)"):
            v = get_v(key)
            return v if v else _(fallback, self.lang)

        sections = []
        field_meta = self._get_field_meta()
        
        def get_lbl(key):
            return field_meta.get(key, (key.replace("_", " ").title(), ""))[0]
        
        # 1. Agrupar Información General
        info_lines = []
        info_group_keys = ["meeting_title", "project_name", "organization_name", "client_name", 
                           "purpose", "objectives", "date", "start_time", "end_time", 
                           "location", "called_by", "chairperson", "secretary", "adjournment_time"]
        
        for k in info_group_keys:
            if k in fields:
                info_lines.append(f"{get_lbl(k)}: {get_val_safe(k)}")
                
        if info_lines:
            sections.append((_("Información General", self.lang), "\n".join(info_lines)))
            
        # 2. Participantes y Ausentes
        parts_keys = ["attendees", "participants"]
        for k in parts_keys:
            if k in fields:
                val = get_v(k)
                asist_str = "\n".join(f"- {p.strip()}" for p in val.split('\n') if p.strip()) if val else _("Sin participantes registrados.", self.lang)
                sections.append((get_lbl(k), asist_str))
                
        if "absentees" in fields:
            val = get_v("absentees")
            aus_str = "\n".join(f"- {p.strip()}" for p in val.split('\n') if p.strip()) if val else _("Sin ausentes registrados.", self.lang)
            sections.append((get_lbl("absentees"), aus_str))
                
        # 3. Transcripción Normalizada
        trans_title = _("Registro de Diálogo de la Sesión", self.lang)
        full_text = self._acta.transcripcion_texto if self._acta and self._acta.transcripcion_texto else ""
        
        if self.normalizer and full_text:
            std_text, _mods = self.normalizer.normalize(full_text)
        else:
            std_text = full_text
            
        if not std_text:
            std_text = _("(Sin transcripción disponible)", self.lang)
            
        sections.append((trans_title, std_text))
        
        # 4. Otras secciones dinámicas en el orden de la plantilla
        handled_keys = set(info_group_keys + parts_keys + ["absentees"])
        for field in fields:
            if field not in handled_keys:
                sections.append((get_lbl(field), get_val_safe(field)))
        
        # 5. Secciones de checkbox
        for key_s, title in [("acuerdos", _("Acuerdos y Compromisos", self.lang)), 
                          ("tareas", _("Tareas y Responsables", self.lang)),
                          ("compromisos", _("Compromisos Pendientes", self.lang)),
                          ("notas", _("Notas Adicionales", self.lang))]:
            
            if getattr(self, f"_cb_{key_s}").get():
                txt_widget = self._section_text_areas.get(key_s)
                content = txt_widget.get("1.0", tk.END).strip() if txt_widget else ""
                if not content: content = _("(Sin contenido redactado)", self.lang)
                sections.append((title, content))

        for i, (title, content) in enumerate(sections, 1):
            exporter.add_section(f"{i}. {title}", content)

             
