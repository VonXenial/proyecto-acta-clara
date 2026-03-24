"""
ActaClara v1.3 – Integración Profesional Final
==============================================
Soporta: Timestamps, Selección de Idioma, Selección de Micro,
Marcado Manual de Modismos y Reproductor Post-Sesión.
"""

import sys
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ── Path Setup ──
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path: sys.path.insert(0, project_root)

from src.ui.styles import apply_styles, COLORS, FONTS
from src.ui.components.sidebar import Sidebar
from src.ui.views.dashboard import DashboardView
from src.ui.views.transcription import TranscriptionView
from src.ui.views.history import HistoryView
from src.ui.views.export import ExportView
from src.ui.views.config import ConfigView
from src.utils.config_manager import ConfigManager
from src.database.db_manager import DBManager
from src.controllers.audio_controller import AudioController
from src.services.stt_engine import STTEngine
from src.services.normalizer import Normalizer
from src.models.acta import Acta

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.theme = self.cfg.get("appearance", "light")
        
        self.title("ActaClara v1.3 Pro - Inteligencia Colectiva")
        self.geometry("1366x768")
        self.resizable(False, False)
        
        self._init_backend()
        self._queue = queue.Queue()
        self.render_ui()
        self._poll_queue()

    def _init_backend(self):
        self.db = DBManager()
        self.db.initialize_db()
        self.audio_ctrl = AudioController()
        self.normalizer = Normalizer()
        self.stt = None 

    def render_ui(self):
        """Re-renderiza con el tema actual y conecta dependencias."""
        for widget in self.winfo_children(): widget.destroy()
        
        self.c = apply_styles(self, theme=self.theme)
        self.configure(bg=self.c["bg"])
        
        # Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_view, theme=self.theme)
        self.sidebar.pack(side="left", fill="y")
        
        # Container principal
        self.container = tk.Frame(self, bg=self.c["bg"])
        self.container.pack(side="left", fill="both", expand=True)
        
        # Vistas
        self.views = {
            "dashboard": DashboardView(self.container, 
                                      on_new_session=lambda: self.show_view("transcription"),
                                      db_manager=self.db, theme=self.theme),
            "transcription": TranscriptionView(self.container, audio_ctrl=self.audio_ctrl,
                                              normalizer=self.normalizer,
                                              on_complete=self._process_audio, theme=self.theme),
            "history": HistoryView(self.container, db_manager=self.db, theme=self.theme),
            "export": ExportView(self.container, theme=self.theme),
            "config": ConfigView(self.container, config_manager=self.cfg, 
                                on_save=self._on_settings_save, theme=self.theme, 
                                audio_ctrl=self.audio_ctrl)
        }
        
        for view in self.views.values(): view.place(relwidth=1, relheight=1)
        self.show_view("dashboard")

    def show_view(self, name: str):
        if name in self.views:
            if hasattr(self.views[name], "refresh_data"): self.views[name].refresh_data()
            self.views[name].lift()
            self.sidebar.set_active(name)

    def _on_settings_save(self):
        new_theme = self.cfg.get("appearance", "light")
        if new_theme != self.theme:
            self.theme = new_theme
            self.render_ui()
        else:
            self.show_view("dashboard")

    def _process_audio(self, file_path, language="auto"):
        def _task():
            try:
                if self.stt is None: self.stt = STTEngine()
                
                # Transcribir con idioma seleccionado
                # (STTEngine actual no acepta idioma en transcribe(), pero Whisper sí. 
                # Mantenemos auto por ahora o actualizamos motor)
                result = self.stt.transcribe(file_path)
                
                # Procesar cada segmento para timestamps
                processed_segments = []
                for seg in result.segmentos:
                    norm_seg, mod_seg = self.normalizer.normalize(seg.texto)
                    processed_segments.append({
                        "start": seg.inicio,
                        "text": norm_seg,
                        "modismos": mod_seg
                    })
                
                # Guardar en DB (Resumen general)
                full_norm, all_mod = self.normalizer.normalize(result.texto_completo)
                acta = Acta(titulo=Path(file_path).stem, idioma=result.idioma_detectado,
                            duracion_segundos=int(result.duracion_procesada or 0), 
                            archivo_audio_ruta=file_path, modismos_detectados=all_mod)
                self.db.insert_acta(acta)
                
                self._queue.put(("RESULT", {"segments": processed_segments, "full_mods": all_mod}))
            except Exception as e: self._queue.put(("ERROR", str(e)))
        threading.Thread(target=_task, daemon=True).start()

    def _poll_queue(self):
        try:
            while True:
                msg_type, data = self._queue.get_nowait()
                if msg_type == "RESULT":
                    tv = self.views["transcription"]
                    tv.txt.configure(state="normal")
                    tv.txt.delete("1.0", tk.END)
                    
                    for child in tv.mod_list.winfo_children(): child.destroy()
                    
                    for seg in data["segments"]:
                        tv.add_segment(seg["start"], seg["text"], seg["modismos"])
                    
                    for m in data["full_mods"]:
                        tv.add_modism_card(m.expresion_original, m.expresion_normalizada)
                    
                    tv.progress_lbl.configure(text="✓ Análisis completo con Timestamps y Modismos.", fg=self.c["success"])
                    tv.progress_bar["value"] = 100
                    tv.rec_btn.configure(state="normal")
                    tv.btn_load.configure(state="normal")
                    tv.btn_next.configure(state="normal")
                elif msg_type == "ERROR": messagebox.showerror("Error de IA", data)
        except queue.Empty: pass
        self.after(100, self._poll_queue)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
