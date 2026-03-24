"""
Vista Transcripción Profesional - ActaClara v1.4
Layout de Alta Fidelidad - Figma Ready
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
from pathlib import Path
from datetime import datetime
from src.ui.styles import COLORS, FONTS, DIMENSIONS
from src.ui.components.tooltip import Tooltip
from src.ui.components.modism_tag import ModismTooltip
from src.ui.components.audio_timeline import AudioTimeline

class TranscriptionView(tk.Frame):
    VIEW_NAME = "transcription"
    
    def __init__(self, parent, audio_ctrl, normalizer, on_complete=None, theme="light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["bg"])
        
        self.audio_ctrl = audio_ctrl
        self.normalizer = normalizer
        self.on_complete = on_complete
        
        self._recording = False
        self._paused = False
        self._audio_path = None
        
        self._build()

    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=self.c["bg"], pady=15, padx=40)
        header.pack(fill="x")

        tk.Label(header, text="Sesión de Transcripción", bg=self.c["bg"], 
                 fg=self.c["text_primary"], font=FONTS["title"]).pack(side="left")

        self.live_indicator = tk.Label(header, text="● EN VIVO", bg=self.c["bg"], 
                                       fg=self.c["live_red"], font=FONTS["badge"])

        # ── Fila de Control Superior (Armonía Figma) ──────────
        ctrl_frame = tk.Frame(self, bg=self.c["card_bg"], padx=30, pady=15,
                              highlightbackground=self.c["border"], highlightthickness=1)
        ctrl_frame.pack(fill="x", padx=40, pady=(0, 10))

        # Grupo 1: Archivos y Grabación
        g1 = tk.Frame(ctrl_frame, bg=self.c["card_bg"])
        g1.pack(side="left")

        ttk.Button(g1, text="📁 Cargar", style="Secondary.TButton", 
                   command=self._on_import_audio, width=10).pack(side="left", padx=5)
        
        self.rec_btn = ttk.Button(g1, text="⏺ Iniciar", style="Primary.TButton", 
                                  command=self._toggle_recording, width=10)
        self.rec_btn.pack(side="left", padx=5)

        # Grupo 2: Idioma (Distancia considerable)
        tk.Frame(ctrl_frame, width=40, bg=self.c["card_bg"]).pack(side="left")
        
        tk.Label(ctrl_frame, text="Idioma:", bg=self.c["card_bg"], 
                 fg=self.c["text_secondary"]).pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value="Español (CL)")
        self.lang_cb = ttk.Combobox(ctrl_frame, textvariable=self.lang_var, 
                                    values=["Auto-detectar", "Español (CL)", "Inglés (US)"], 
                                    state="readonly", width=15)
        self.lang_cb.pack(side="left")

        # Grupo 3: Timeline y Play (Derecha)
        self.timeline_container = tk.Frame(ctrl_frame, bg=self.c["card_bg"])
        self.timeline_container.pack(side="right", fill="x", expand=True, padx=(40, 0))
        
        self.timeline = AudioTimeline(self.timeline_container, duration=0, theme="light")
        self.timeline.pack(fill="x")

        # ── Cuerpo Central ────────────────────────────────────
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
        tk.Label(header_l, text="Transcripción Detallada", bg=self.c["card_bg"], 
                 fg=self.c["text_primary"], font=FONTS["heading"]).pack(side="left")
        
        ttk.Button(header_l, text="✨ Marcar Modismo", style="Secondary.TButton",
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
        
        tk.Label(right_card, text="Modismos Detectados", bg=self.c["card_bg"], 
                 fg=self.c["text_primary"], font=FONTS["heading"]).pack(anchor="w", pady=(0, 10))

        # Scrollable Frame para Modismos
        self.scroll_canvas = tk.Canvas(right_card, bg=self.c["card_bg"], highlightthickness=0)
        self.mod_list = tk.Frame(self.scroll_canvas, bg=self.c["card_bg"])
        
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_canvas.create_window((0,0), window=self.mod_list, anchor="nw")
        
        # Vincular rueda del ratón
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.mod_list.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        # ── Fila de Acción Inferior ───────────────────────────
        action_frame = tk.Frame(self, bg=self.c["bg"], padx=40, pady=15)
        action_frame.pack(fill="x")

        self.pause_btn = ttk.Button(action_frame, text="⏸ Pausar Grabación", style="Secondary.TButton", 
                                    command=self._toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=5)

        self.cancel_btn = ttk.Button(action_frame, text="✕ Cancelar", style="Secondary.TButton", 
                                     command=self._cancel_session, state="disabled")
        self.cancel_btn.pack(side="left", padx=5)

        self.btn_next = ttk.Button(action_frame, text="Continuar a Normalización →", 
                                   style="Success.TButton", state="disabled", command=self._go_to_export)
        self.btn_next.pack(side="right")

        # Barra de progreso final
        self.progress_bar = ttk.Progressbar(self, style="Blue.Horizontal.TProgressbar", mode="determinate")
        self.progress_bar.pack(fill="x", padx=40, pady=(0, 10))

        self.txt.tag_bind("modismo", "<Button-1>", self._on_modismo_click)

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _refresh_mics(self):
        mics = self.audio_ctrl.get_microphones()
        # No hay combo de micro en esta vista según el nuevo layout, pero lo mantenemos interno
        self._available_mics = mics

    def _toggle_recording(self):
        if not self._recording:
            self._recording = True
            self.rec_btn.configure(text="⏹ Detener", style="Danger.TButton")
            self.pause_btn.configure(state="normal")
            self.cancel_btn.configure(state="normal")
            self.live_indicator.pack(side="left", padx=15)
            self.audio_ctrl.start_recording() # Por defecto usa el micro 0 o el configurado
        else:
            if messagebox.askyesno("ActaClara", "¿Deseas detener la grabación y procesar el acta?"):
                self._stop_and_process()

    def _stop_and_process(self):
        self._recording = False
        self.rec_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        
        path = f"data/audios_prueba/grabacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        self.audio_ctrl.stop_recording(path)
        self._audio_path = path
        
        self.live_indicator.pack_forget()
        self.progress_bar["value"] = 30
        
        if self.on_complete: self.on_complete(path, self.lang_var.get())

    def _toggle_pause(self):
        if not self._paused:
            self.audio_ctrl.pause_recording()
            self.pause_btn.configure(text="▶ Reanudar")
            self._paused = True
        else:
            self.audio_ctrl.resume_recording()
            self.pause_btn.configure(text="⏸ Pausar")
            self._paused = False

    def _cancel_session(self):
        if messagebox.askyesno("Confirmar", "¿Deseas descartar la grabación actual?"):
            self._recording = False
            self.audio_ctrl.stop_recording("data/audios_prueba/discarded.wav")
            self.rec_btn.configure(text="⏺ Iniciar", style="Primary.TButton", state="normal")
            self.pause_btn.configure(state="disabled", text="⏸ Pausar")
            self.cancel_btn.configure(state="disabled")
            self.live_indicator.pack_forget()
            self.progress_bar["value"] = 0

    def _on_import_audio(self):
        file = filedialog.askopenfilename(filetypes=[("Audios", "*.wav *.mp3 *.m4a")])
        if file:
            if self.on_complete: self.on_complete(file, self.lang_var.get())

    def _mark_selected_as_idiom(self):
        try:
            sel = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if not sel: return
            
            win = tk.Toplevel(self)
            win.title("Enseñar Modismo a la IA")
            win.geometry("450x350")
            win.configure(bg=self.c["card_bg"])
            win.transient(self)
            
            tk.Label(win, text=f"Expresión seleccionada: '{sel}'", font=FONTS["heading"], 
                     bg=self.c["card_bg"], fg=self.c["primary"]).pack(pady=15)
            
            container = tk.Frame(win, bg=self.c["card_bg"], padx=20)
            container.pack(fill="both")

            # Traducción
            tk.Label(container, text="Traducción formal:", bg=self.c["card_bg"]).grid(row=0, column=0, sticky="w")
            ent_neutral = ttk.Entry(container, width=35)
            ent_neutral.grid(row=0, column=1, pady=10)

            # Categoría
            tk.Label(container, text="Categoría:", bg=self.c["card_bg"]).grid(row=1, column=0, sticky="w")
            cat_cb = ttk.Combobox(container, values=["Opinion", "Tiempo", "Acuerdo", "Acción", "Evaluación"], width=32)
            cat_cb.grid(row=1, column=1, pady=10)
            cat_cb.current(0)

            # Ejemplo
            tk.Label(container, text="Ejemplo de uso:", bg=self.c["card_bg"]).grid(row=2, column=0, sticky="w")
            ent_example = ttk.Entry(container, width=35)
            ent_example.grid(row=2, column=1, pady=10)

            def _save():
                if ent_neutral.get():
                    self.normalizer.add_new_idiom(sel, ent_neutral.get())
                    win.destroy()
                    self._rehighlight_all()
                    messagebox.showinfo("ActaClara", "Modismo guardado en el diccionario local.")

            ttk.Button(win, text="💾 Guardar en Diccionario", style="Primary.TButton", command=_save).pack(pady=20)
        except tk.TclError:
            messagebox.showwarning("Selección", "Primero selecciona las palabras con el mouse.")

    def add_segment(self, start_time, text, modismos):
        self.txt.configure(state="normal")
        ts = f"[{int(start_time // 60):02d}:{int(start_time % 60):02d}] "
        
        start_idx = self.txt.index(tk.END)
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
                        ModismTooltip(self, mod_text, "Ver sugerencia", (x, y))
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
        self.master.master.show_view("export")

    def add_modism_card(self, original, normalizado):
        f = tk.Frame(self.mod_list, bg="#FFF3E0", padx=12, pady=10, 
                     highlightbackground="#FF8C00", highlightthickness=1)
        f.pack(fill="x", pady=5, padx=10)
        tk.Label(f, text=f'"{original}"', bg="#FFF3E0", fg="#FF8C00", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(f, text=f"→ {normalizado}", bg="#FFF3E0", fg=self.c["text_secondary"], 
                 font=FONTS["small"], wraplength=150, justify="left").pack(anchor="w")
        Tooltip(f, title=original, body=f"Equivalente formal: {normalizado}")
