"""
Vista Transcripción Profesional - ActaClara v1.4
Layout de Alta Fidelidad - Figma Ready
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
from datetime import datetime
from typing import Optional, List, Any

from src.utils.i18n import translate as _  # type: ignore
# Importaciones relativas para mejor resolución por el linter
from src.ui.styles import COLORS, FONTS # type: ignore
from src.ui.components.tooltip import Tooltip # type: ignore
from src.ui.components.modism_tag import ModismTooltip # type: ignore
from src.ui.components.audio_timeline import AudioTimeline # type: ignore
from src.config import RECORDINGS_DIR # type: ignore

class TranscriptionView(tk.Frame):
    VIEW_NAME = "transcription"
    
    def __init__(self, parent, audio_ctrl, normalizer, config_manager=None, on_complete=None, theme="light", lang="Español"):
        self.c = COLORS[theme]
        self.lang = lang
        super().__init__(parent, bg=self.c["bg"])
        
        self.audio_ctrl = audio_ctrl
        self.normalizer = normalizer
        self.cfg = config_manager
        self.on_complete = on_complete
        
        self._recording = False
        self._paused = False
        self._audio_path: Optional[str] = None
        self.theme = theme
        
        # Inicialización de atributos UI para evitar errores de tipo
        self.live_indicator: tk.Label = None # type: ignore
        self.rec_btn: ttk.Button = None # type: ignore
        self.lang_var: tk.StringVar = None # type: ignore
        self.lang_cb: ttk.Combobox = None # type: ignore
        self.timeline_container: tk.Frame = None # type: ignore
        self.timeline: AudioTimeline = None # type: ignore
        self.progress_bar: ttk.Progressbar = None # type: ignore
        self.progress_lbl: tk.Label = None # type: ignore
        self.pause_btn: ttk.Button = None # type: ignore
        self.cancel_btn: ttk.Button = None # type: ignore
        self.btn_next: ttk.Button = None # type: ignore
        self.txt: tk.Text = None # type: ignore
        self.scroll_canvas: tk.Canvas = None # type: ignore
        self.canvas_window: int = None # type: ignore
        self.mod_list: tk.Frame = None # type: ignore
        self._available_mics: List[Any] = []
        self.current_acta_id: Optional[int] = None
        
        self._build()

    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=self.c["bg"], pady=15, padx=40)
        header.pack(fill="x")

        tk.Label(header, text=_("Sesión de Transcripción", self.lang), bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")

        self.live_indicator = tk.Label(header, text=_("● EN VIVO", self.lang), bg=self.c["bg"], 
                                       fg=self.c["live_red"], font=FONTS["badge"])

        # ── Fila de Control Superior (Armonía Figma) ──────────
        ctrl_frame = tk.Frame(self, bg=self.c["card_bg"], padx=30, pady=15,
                              highlightbackground=self.c["border"], highlightthickness=1)
        ctrl_frame.pack(fill="x", padx=40, pady=(0, 10))

        # Grupo 1: Archivos y Grabación
        g1 = tk.Frame(ctrl_frame, bg=self.c["card_bg"])
        g1.pack(side="left")

        ttk.Button(g1, text=_("📁 Cargar", self.lang), style="Secondary.TButton", 
                   command=self._on_import_audio, width=10).pack(side="left", padx=5)
        
        self.rec_btn = ttk.Button(g1, text=_("⏺ Iniciar", self.lang), style="Primary.TButton", 
                                  command=self._toggle_recording, width=10)
        self.rec_btn.pack(side="left", padx=5)

        # Grupo 2: Idioma (Distancia considerable)
        tk.Frame(ctrl_frame, width=40, bg=self.c["card_bg"]).pack(side="left")
        
        tk.Label(ctrl_frame, text=_("Idioma:", self.lang), bg=self.c["card_bg"], 
                 fg=self.c["text_secondary"]).pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value=_("Español (CL)", self.lang))
        self.lang_cb = ttk.Combobox(ctrl_frame, textvariable=self.lang_var, 
                                    values=[_("Auto-detectar", self.lang), _("Español (CL)", self.lang), _("Inglés (US)", self.lang)], 
                                    state="readonly", width=15)
        self.lang_cb.pack(side="left")

        # Grupo 3: Timeline y Play (Derecha)
        self.timeline_container = tk.Frame(ctrl_frame, bg=self.c["card_bg"])
        self.timeline_container.pack(side="right", fill="x", expand=True, padx=(40, 0))
        
        self.timeline = AudioTimeline(self.timeline_container, audio_ctrl=self.audio_ctrl, theme=self.theme)
        self.timeline.pack(fill="x")

        # ── Pack bottom elements FIRST (so body expand doesn't hide them) ──

        # Barra de progreso con etiqueta de estado (bottom-most)
        progress_frame = tk.Frame(self, bg=self.c["bg"], padx=40)
        progress_frame.pack(side="bottom", fill="x", pady=(0, 8))
        
        self.progress_bar = ttk.Progressbar(progress_frame, style="Blue.Horizontal.TProgressbar", 
                                            mode="determinate", length=300)
        self.progress_bar.pack(fill="x")
        
        self.progress_lbl = tk.Label(progress_frame, text="", bg=self.c["bg"], 
                                     fg=self.c["text_secondary"], font=FONTS["small"], anchor="w")
        self.progress_lbl.pack(fill="x", pady=(3, 0))

        # Fila de Acción Inferior
        action_frame = tk.Frame(self, bg=self.c["bg"], padx=40, pady=8)
        action_frame.pack(side="bottom", fill="x")

        self.pause_btn = ttk.Button(action_frame, text=_("⏸ Pausar Grabación", self.lang), style="Secondary.TButton", 
                                    command=self._toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=5)

        self.cancel_btn = ttk.Button(action_frame, text=_("✕ Cancelar", self.lang), style="Secondary.TButton", 
                                     command=self._cancel_session, state="disabled")
        self.cancel_btn.pack(side="left", padx=5)

        self.btn_next = ttk.Button(action_frame, text=_("Ir a Exportar Documento →", self.lang), 
                                   style="Success.TButton", state="disabled", command=self._go_to_export)
        self.btn_next.pack(side="right")

        # ── Cuerpo Central (expands into remaining space) ─────
        body = tk.Frame(self, bg=self.c["bg"])
        body.pack(fill="both", expand=True, padx=40, pady=5)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Columna Izquierda: Transcripción con Scroll
        left_card = tk.Frame(body, bg=self.c["card_bg"], padx=20, pady=20,
                             highlightbackground=self.c["border"], highlightthickness=1)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        header_l = tk.Frame(left_card, bg=self.c["card_bg"])
        header_l.pack(fill="x", pady=(0, 10))
        tk.Label(header_l, text=_("Transcripción Detallada", self.lang), bg=self.c["card_bg"], 
                 fg=self.c["text_primary"], font=FONTS["heading"]).pack(side="left")
        
        ttk.Button(header_l, text=_("✨ Marcar Modismo", self.lang), style="Secondary.TButton",
                   command=self._mark_selected_as_idiom).pack(side="right")

        self.txt = tk.Text(left_card, font=FONTS["body"], bg="white", relief="flat", 
                           wrap="word", padx=15, pady=15, spacing2=5)
        self.txt.pack(fill="both", expand=True)
        self.txt.tag_configure("modismo", background="#FFFF00", foreground="black", font=("Segoe UI", 10, "bold"))
        self.txt.tag_configure("timestamp", foreground=self.c["text_secondary"], font=FONTS["small"])

        # Columna Derecha: Modismos con Scroll "Invisible"
        right_card = tk.Frame(body, bg=self.c["card_bg"], padx=15, pady=20,
                              highlightbackground=self.c["border"], highlightthickness=1)
        right_card.grid(row=0, column=1, sticky="nsew")
        
        tk.Label(right_card, text=_("Modismos Detectados", self.lang), bg=self.c["card_bg"], 
                 fg=self.c["text_primary"], font=FONTS["heading"]).pack(anchor="w", pady=(0, 10))

        # Scrollable Frame para Modismos
        self.scroll_canvas = tk.Canvas(right_card, bg=self.c["card_bg"], highlightthickness=0)
        self.mod_list = tk.Frame(self.scroll_canvas, bg=self.c["card_bg"])
        
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.scroll_canvas.create_window((0,0), window=self.mod_list, anchor="nw")
        
        # Sincronizar el ancho del frame con el canvas para que el scroll funcione en toda el área
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Vincular rueda del ratón (Solo cuando el mouse está sobre la lista para evitar conflictos)
        def _on_enter_scroll(e):
            self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self.scroll_canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.scroll_canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        def _on_leave_scroll(e):
            self.scroll_canvas.unbind_all("<MouseWheel>")
            self.scroll_canvas.unbind_all("<Button-4>")
            self.scroll_canvas.unbind_all("<Button-5>")

        self.scroll_canvas.bind("<Enter>", _on_enter_scroll)
        self.scroll_canvas.bind("<Leave>", _on_leave_scroll)
        
        self.mod_list.bind("<Configure>", self._update_scroll_region)

        self.txt.tag_bind("modismo", "<Button-1>", self._on_modismo_click)

    def _on_canvas_configure(self, event):
        # Ajustar el ancho del frame interno al ancho del canvas
        self.scroll_canvas.itemconfig(self.canvas_window, width=event.width)

    def _update_scroll_region(self, event=None):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        # Manejar diferentes plataformas (Linux/Windows)
        if event.num == 4: # Linux Scroll Up
            self.scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux Scroll Down
            self.scroll_canvas.yview_scroll(1, "units")
        else: # Windows
            self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _refresh_mics(self):
        mics = self.audio_ctrl.get_microphones()
        # No hay combo de micro en esta vista según el nuevo layout, pero lo mantenemos interno
        self._available_mics = mics

    def _toggle_recording(self):
        if not self._recording:
            self._recording = True
            self.rec_btn.configure(text=_("⏹ Detener", self.lang), style="Danger.TButton")
            self.pause_btn.configure(state="normal")
            self.cancel_btn.configure(state="normal")
            self.live_indicator.pack(side="left", padx=15)
            self.audio_ctrl.start_recording() # Por defecto usa el micro 0 o el configurado
        else:
            if messagebox.askyesno(_("ActaClara", self.lang), _("¿Deseas detener la grabación y procesar el acta?", self.lang)):
                self._stop_and_process()

    def _stop_and_process(self):
        self._recording = False
        self.rec_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        
        os.makedirs(RECORDINGS_DIR, exist_ok=True)
        path = os.path.join(RECORDINGS_DIR, f"grabacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        self.audio_ctrl.stop_recording(path)
        self._audio_path = path
        self.timeline.set_audio(path)
        
        self.live_indicator.pack_forget()
        self.progress_lbl.configure(text=_("⏳ Guardando audio y preparando transcripción...", self.lang), fg=self.c["primary"])
        self.progress_bar["value"] = 10
        
        if self.on_complete:
            self.on_complete(path, self.lang_var.get())

    def _toggle_pause(self):
        if not self._paused:
            self.audio_ctrl.pause_recording()
            self.pause_btn.configure(text=_("▶ Reanudar", self.lang))
            self._paused = True
        else:
            self.audio_ctrl.resume_recording()
            self.pause_btn.configure(text=_("⏸ Pausar", self.lang))
            self._paused = False

    def _cancel_session(self):
        if self._recording:
            # Durante grabación activa → guardar audio y confirmar
            backup_name = f"grabacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            backup_path = os.path.join(RECORDINGS_DIR, backup_name)
            
            msg = _("¿Estás seguro de que deseas cancelar la sesión?\n\nEl audio grabado se guardará en la carpeta de grabaciones:\n📁 {recordings_dir}/{backup_name}\n\nLa transcripción y los modismos detectados se eliminarán.", self.lang)
            confirm = messagebox.askyesno(
                _("Confirmar cancelación", self.lang),
                msg.format(recordings_dir=RECORDINGS_DIR, backup_name=backup_name)
            )
            if not confirm:
                return
            
            self.audio_ctrl.stop_recording(backup_path)
            self._recording = False
            self._paused = False
            self._audio_path = backup_path
            self.live_indicator.pack_forget()
            
            msg2 = _("La sesión fue cancelada.\n\nTu audio fue guardado en:\n📁 {backup_path}", self.lang)
            messagebox.showinfo(
                _("Sesión cancelada", self.lang),
                msg2.format(backup_path=backup_path)
            )
        else:
            # Post-transcripción → limpiar resultados
            confirm = messagebox.askyesno(
                _("Limpiar sesión", self.lang),
                _("¿Deseas limpiar la transcripción actual y empezar de nuevo?\n\nLos resultados se eliminarán, pero el audio original permanece guardado.", self.lang)
            )
            if not confirm:
                return
        
        # Resetear controles (ambos caminos)
        self.rec_btn.configure(text=_("⏺ Iniciar", self.lang), style="Primary.TButton", state="normal")
        self.pause_btn.configure(state="disabled", text=_("⏸ Pausar Grabación", self.lang))
        self.cancel_btn.configure(state="disabled", text=_("✕ Cancelar", self.lang))
        self.btn_next.configure(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_lbl.configure(text="", fg=self.c["text_secondary"])
        self.current_acta_id = None
        
        # Limpiar Transcripción Detallada
        self.txt.configure(state="normal")
        self.txt.delete("1.0", tk.END)
        self.txt.configure(state="disabled")
        
        # Limpiar Modismos Detectados
        for widget in self.mod_list.winfo_children():
            widget.destroy()

    def _on_import_audio(self):
        if not os.path.exists(RECORDINGS_DIR):
            os.makedirs(RECORDINGS_DIR, exist_ok=True)
            
        file = filedialog.askopenfilename(
            title=_("Continuar sesión / Cargar Audio", self.lang),
            initialdir=RECORDINGS_DIR,
            filetypes=[("Audios", "*.wav *.mp3 *.m4a")]
        )
        if file:
            self.progress_lbl.configure(text=_("⏳ Cargando audio y preparando transcripción...", self.lang), fg=self.c["primary"])
            self.progress_bar["value"] = 10
            self._audio_path = file
            self.timeline.set_audio(file)
            if self.on_complete: self.on_complete(file, self.lang_var.get())

    def _mark_selected_as_idiom(self):
        try:
            # 1. Obtener selección original
            sel_orig = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if not sel_orig:
                return

            # 2. LIMPIEZA INTELIGENTE:
            # - Quitar marcas de tiempo [00:00]
            # - Quitar puntuación innecesaria al inicio/final (puntos, comas, signos de interrogación)
            # - Normalizar espacios
            sel_clean = re.sub(r'\[\d{1,2}:\d{2}\]', '', sel_orig)
            sel_clean = re.sub(r'^[\s\.,\?!\(\) "¿¡]+', '', sel_clean) # Limpiar inicio
            sel_clean = re.sub(r'[\s\.,\?!\(\) "¡?]+$', '', sel_clean) # Limpiar final
            sel_clean = " ".join(sel_clean.split())
            
            if not sel_clean:
                return

            # 3. Validar longitud (máximo 5 palabras)
            palabras = sel_clean.split()
            if len(palabras) > 5:
                sel = " ".join(palabras[:5])
            else:
                sel = sel_clean
            
            # 4. Verificar duplicados
            exists = any(m["expresion_original"].lower() == sel.lower() for m in self.normalizer.modismos_dict)
            if exists:
                messagebox.showinfo(
                    _("ActaClara", self.lang), 
                    _("El modismo '{sel}' ya existe en el diccionario.", self.lang).format(sel=sel)
                )
                return

            # 5. Crear Modal Rediseñado
            win = tk.Toplevel(self)
            win.title(_("Enseñar Modismo", self.lang))
            win.geometry("500x480")
            win.configure(bg=self.c["card_bg"])
            win.resizable(False, False)
            win.transient(self.winfo_toplevel())
            win.grab_set() # Modal real

            # Centrar modal respecto a la app
            app_x = self.winfo_toplevel().winfo_x()
            app_y = self.winfo_toplevel().winfo_y()
            win.geometry(f"+{app_x + 430}+{app_y + 150}")

            # Header estilizado
            header = tk.Frame(win, bg=self.c["primary"], height=60)
            header.pack(fill="x")
            header.pack_propagate(False)
            
            tk.Label(header, text="🇨🇱  " + _("Enseñar nuevo modismo", self.lang), 
                     font=FONTS["heading"], bg=self.c["primary"], fg="white").pack(pady=15)

            main_frame = tk.Frame(win, bg=self.c["card_bg"], padx=30, pady=20)
            main_frame.pack(fill="both", expand=True)

            # Campo: Expresión (Solo lectura para confirmar)
            tk.Label(main_frame, text=_("Expresión seleccionada:", self.lang), 
                     bg=self.c["card_bg"], fg=self.c["text_secondary"], font=FONTS["small"]).pack(anchor="w")
            ent_orig = ttk.Entry(main_frame, width=50)
            ent_orig.insert(0, sel)
            ent_orig.configure(state="readonly")
            ent_orig.pack(pady=(0, 15))

            # Campo: Traducción Neutral
            tk.Label(main_frame, text=_("Traducción / Significado formal:", self.lang), 
                     bg=self.c["card_bg"], fg=self.c["text_primary"], font=FONTS["body"]).pack(anchor="w")
            ent_neutral = ttk.Entry(main_frame, width=50)
            ent_neutral.pack(pady=(0, 15))
            ent_neutral.focus_set()

            # Fila: Categoría
            tk.Label(main_frame, text=_("Categoría:", self.lang), 
                     bg=self.c["card_bg"], fg=self.c["text_primary"], font=FONTS["body"]).pack(anchor="w")
            cat_cb = ttk.Combobox(main_frame, values=[
                _("Opinion", self.lang), _("Tiempo", self.lang), _("Acuerdo", self.lang), 
                _("Acción", self.lang), _("Evaluación", self.lang), _("Lugar", self.lang)
            ], state="readonly", width=47)
            cat_cb.pack(pady=(0, 15))
            cat_cb.current(0)

            # Campo: Ejemplo
            tk.Label(main_frame, text=_("Ejemplo de uso (opcional):", self.lang), 
                     bg=self.c["card_bg"], fg=self.c["text_primary"], font=FONTS["body"]).pack(anchor="w")
            ent_example = ttk.Entry(main_frame, width=50)
            ent_example.pack(pady=(0, 20))

            def _on_save():
                val_neutral = ent_neutral.get().strip()
                if not val_neutral:
                    messagebox.showwarning(_("Error", self.lang), _("Debes ingresar una traducción formal.", self.lang))
                    return
                
                # Guardar con la nueva estructura extendida
                self.normalizer.add_new_idiom(
                    original=sel, 
                    normalizada=val_neutral,
                    categoria=cat_cb.get().lower(),
                    ejemplos=[ent_example.get().strip()] if ent_example.get().strip() else []
                )
                
                win.destroy()
                self._rehighlight_all() # Actualizar vista actual
                
                # Feedback visual
                msg_success = _("Modismo '{sel}' guardado correctamente.", self.lang).format(sel=sel)
                self.progress_lbl.configure(text="✓ " + msg_success, fg=self.c["success"])

            # Footer con botones
            btn_frame = tk.Frame(main_frame, bg=self.c["card_bg"])
            btn_frame.pack(fill="x", pady=10)
            
            ttk.Button(btn_frame, text=_("Cancelar", self.lang), style="Secondary.TButton", 
                       command=win.destroy).pack(side="left")
            ttk.Button(btn_frame, text=_("💾 Guardar", self.lang), style="Primary.TButton", 
                       command=_on_save).pack(side="right")

        except tk.TclError:
            messagebox.showwarning(_("Selección", self.lang), _("Selecciona las palabras en el texto para enseñarlas a la IA.", self.lang))


    def add_segment(self, start_time, text, modismos):
        self.txt.configure(state="normal")
        
        # Insertar timestamp opcionalmente según configuración
        show_ts = True
        if self.cfg:
            show_ts = self.cfg.get("timestamps", True)
            
        if show_ts:
            ts = f"[{int(start_time // 60):02d}:{int(start_time % 60):02d}] "
            self.txt.insert(tk.END, ts, "timestamp")
        
        text_insertion_point = self.txt.index(tk.END)
        self.txt.insert(tk.END, text + "\n\n")
        
        # Resaltar modismos
        for m in self.normalizer.modismos_dict:
            pattern = r'\b' + re.escape(m["expresion_original"]) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                s = self.txt.index(f"{text_insertion_point} + {match.start()} chars")
                e = self.txt.index(f"{text_insertion_point} + {match.end()} chars")
                self.txt.tag_add("modismo", s, e)
        
        self.txt.configure(state="disabled")
        self.txt.see(tk.END)

    def _on_modismo_click(self, event):
        index = self.txt.index(f"@{event.x},{event.y}")
        tags = self.txt.tag_names(index)
        if "modismo" in tags:
            ranges = self.txt.tag_ranges("modismo")
            for i in range(0, len(ranges), 2):
                start, end = ranges[i], ranges[i+1]
                if self.txt.compare(index, ">=", start) and self.txt.compare(index, "<=", end):
                    mod_text = self.txt.get(start, end)
                    bbox = self.txt.bbox(start)
                    if bbox:
                        x = self.txt.winfo_rootx() + bbox[0]
                        y = self.txt.winfo_rooty() + bbox[1] + bbox[3]
                        ModismTooltip(self, mod_text, _("Ver sugerencia", self.lang), (x, y))
                    break

    def _rehighlight_all(self):
        content = self.txt.get("1.0", tk.END)
        self.txt.configure(state="normal")
        self.txt.tag_remove("modismo", "1.0", tk.END)
        for m in self.normalizer.modismos_dict:
            pattern = r'\b' + re.escape(m["expresion_original"]) + r'\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                s = self.txt.index(f"1.0 + {match.start()} chars")
                e = self.txt.index(f"1.0 + {match.end()} chars")
                self.txt.tag_add("modismo", s, e)
        self.txt.configure(state="disabled")

    def _go_to_export(self):
        # Usar forma más robusta de acceder al método show_view de la ventana principal
        target = self.master
        while target and not hasattr(target, "show_view"):
            target = target.master
        
        if target:
            target.show_view("export", context={"acta_id": self.current_acta_id}) # type: ignore

    def add_modism_card(self, original, normalizado):
        f = tk.Frame(self.mod_list, bg="#FFF3E0", padx=12, pady=10, 
                     highlightbackground="#FF8C00", highlightthickness=1)
        f.pack(fill="x", pady=5, padx=10)
        tk.Label(f, text=f'"{original}"', bg="#FFF3E0", fg="#FF8C00", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(f, text=f"→ {normalizado}", bg="#FFF3E0", fg=self.c["text_secondary"], 
                 font=FONTS["small"], wraplength=150, justify="left").pack(anchor="w")
        # Tooltip eliminado por solicitud del usuario
