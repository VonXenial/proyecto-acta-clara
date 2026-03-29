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
from tkinter import messagebox
import logging
from pathlib import Path
from src.utils.i18n import translate as _  # type: ignore

# ── Path Setup ──
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.styles import apply_styles # type: ignore
from src.ui.components.sidebar import Sidebar # type: ignore
from src.ui.views.dashboard import DashboardView # type: ignore
from src.ui.views.transcription import TranscriptionView # type: ignore
from src.ui.views.history import HistoryView # type: ignore
from src.ui.views.export import ExportView # type: ignore
from src.ui.views.config import ConfigView # type: ignore
logger = logging.getLogger("MainWindow")
from src.utils.config_manager import ConfigManager # type: ignore
from src.database.db_manager import DBManager # type: ignore
from src.controllers.audio_controller import AudioController # type: ignore
from src.services.stt_engine import STTEngine # type: ignore
from src.services.normalizer import Normalizer # type: ignore
from src.models.acta import Acta # type: ignore
from typing import Optional, Dict, Any

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.theme = self.cfg.get("appearance", "light")
        self.lang = self.cfg.get("lang_ui", "Español")
        scale = self.cfg.get("font_size", "mediano")
        from src.ui.styles import set_font_scale  # type: ignore
        set_font_scale(scale)
        
        # Configurar logging según preferencia
        self._setup_logging()
        
        self.title(_("ActaClara v1.4 Pro - Inteligencia Colectiva", self.lang))
        self.geometry("1366x768")
        self.resizable(False, False)
        
        # Icono de la aplicación (Resolución estricta para Windows 11 y soporte a PyInstaller)
        try:
            from pathlib import Path
            import sys
            from src.config import APP_DIR
            
            root = Path(APP_DIR)
            
            if sys.platform == "win32":
                # En Windows, usar iconbitmap con default= fuerza la actualización global
                ico_path = root / "assets" / "logo" / "logo_icon_64px.ico"
                if ico_path.exists():
                    self.iconbitmap(default=str(ico_path))
            else:
                # En Linux/Mac, usar iconphoto
                png_path = root / "assets" / "logo" / "logo_icon_64px.png"
                if png_path.exists():
                    self._main_icon_image = tk.PhotoImage(file=str(png_path))
                    self.iconphoto(False, self._main_icon_image)
                    
        except Exception as e:
            logger.warning(f"Fallo general en la carga de iconos: {e}")
        
        
        # Inicialización de atributos para el linter
        self.db: DBManager = None # type: ignore
        self.audio_ctrl: AudioController = None # type: ignore
        self.normalizer: Normalizer = None # type: ignore
        self.stt: Optional[STTEngine] = None
        self.c: Dict[str, str] = {}
        self.sidebar: Sidebar = None # type: ignore
        self.container: tk.Frame = None # type: ignore
        self.views: Dict[str, Any] = {}
        
        self._init_backend()
        self._queue: queue.Queue = queue.Queue()
        
        # Ejecutar mantenimiento en segundo plano tras iniciar
        self.after(2000, self._run_system_maintenance)
        
        # Estado del temporizador
        self._processing_start = 0.0
        self._is_processing = False
        self._current_msg = ""
        
        self.render_ui()
        self._poll_queue()
        self._update_timer()

    def _update_timer(self):
        """Bucle de actualización para el contador de tiempo real."""
        if self._is_processing and self._processing_start > 0:
            import time as _time
            elapsed = int(_time.time() - self._processing_start)
            m, s = divmod(elapsed, 60)
            time_str = f"{m:02d}:{s:02d}"
            
            # Actualizar label en la vista de transcripción si existe
            if "transcription" in self.views:
                tv = self.views["transcription"]
                if hasattr(tv, "progress_lbl"):
                    tv.progress_lbl.configure(text=f"{self._current_msg} ({time_str})")
        
        self.after(1000, self._update_timer)

    def _init_backend(self):
        self.db = DBManager()
        self.db.initialize_db()
        from src.config import FFMPEG_PATH
        self.audio_ctrl = AudioController(ffmpeg_path=FFMPEG_PATH)
        self.normalizer = Normalizer()
        self.stt = None 

    def render_ui(self):
        """Re-renderiza con el tema actual y conecta dependencias."""
        for widget in self.winfo_children():
            widget.destroy()
        
        self.c = apply_styles(self, theme=self.theme)
        self.configure(bg=self.c["bg"])
        
        # Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_view, theme=self.theme, lang=self.lang)
        self.sidebar.pack(side="left", fill="y")
        
        # Container principal
        self.container = tk.Frame(self, bg=self.c["bg"])
        self.container.pack(side="left", fill="both", expand=True)
        
        # Vistas
        self.views = {
            "dashboard": DashboardView(self.container, 
                                      on_new_session=lambda: self.show_view("transcription"),
                                      db_manager=self.db, theme=self.theme, lang=self.lang,
                                      app=self),
            "transcription": TranscriptionView(self.container, audio_ctrl=self.audio_ctrl,
                                              normalizer=self.normalizer,
                                              config_manager=self.cfg,
                                              on_complete=self._process_audio, theme=self.theme, lang=self.lang),
            "history": HistoryView(self.container, db_manager=self.db, theme=self.theme, app=self, lang=self.lang),
            "export": ExportView(self.container, theme=self.theme, lang=self.lang, 
                                 app=self, db_manager=self.db, config_manager=self.cfg,
                                 normalizer=self.normalizer),
            "config": ConfigView(self.container, config_manager=self.cfg, 
                                 on_save=self._on_settings_save, theme=self.theme, 
                                 audio_ctrl=self.audio_ctrl)
        }
        
        for view in self.views.values():
            view.place(relwidth=1, relheight=1)
        self.show_view("dashboard")

    def show_view(self, name: str, context=None):
        if name in self.views:
            if hasattr(self.views[name], "set_context") and context is not None:
                self.views[name].set_context(context)
            if hasattr(self.views[name], "refresh_data"):
                self.views[name].refresh_data()
            self.views[name].lift()
            self.sidebar.set_active(name)

    def _on_settings_save(self):
        # Guardar valores actuales para detectar cambios que requieran reiniciar motores
        old_model = self.cfg.get("whisper_model")
        old_device = self.cfg.get("proc_mode")

        new_theme = self.cfg.get("appearance", "light")
        new_scale = self.cfg.get("font_size", "mediano")
        new_lang = self.cfg.get("lang_ui", "Español")
        
        # Si cambiaron ajustes críticos de IA, forzamos recarga del motor en el próximo proceso
        if old_model != self.cfg.get("whisper_model") or old_device != self.cfg.get("proc_mode"):
            self.stt = None
            logger.info("Ajustes de IA cambiados. El motor se recargará en la próxima transcripción.")

        from src.ui.styles import set_font_scale  # type: ignore
        set_font_scale(new_scale)
        
        self.theme = new_theme
        self.lang = new_lang
        self.render_ui()
        self.show_view("config")

    def _process_audio(self, file_path, language="auto"):
        self._processing_start = 0.0 # Se seteará dentro de _task
        self._is_processing = True
        self._current_msg = _("⏳ Iniciando...", self.lang)
        
        # Leer ajustes de configuración
        stt_model = self.cfg.get("whisper_model", "small")
        # Mapeo robusto para evitar errores de UI strings en la config
        raw_device = self.cfg.get("proc_mode", "auto")
        device_map = {
            "Automático (recomendado)": "auto",
            "CPU (predeterminado)": "cpu",
            "GPU (si disponible)": "cuda"
        }
        device = device_map.get(raw_device, raw_device)
        
        do_diarize = self.cfg.get("diarize", True)
        auto_norm = self.cfg.get("auto_normalize", True)
        
        # Ajustar calidad de audio (sample rate) antes de grabar
        quality = self.cfg.get("audio_quality", "Alta (16kHz)")
        sr_map = {
            "Alta (16kHz, recomendado)": 16000,
            "Alta (16kHz)": 16000,
            "Media (8kHz)": 8000,
            "Baja (para audios largos)": 8000
        }
        target_sr = sr_map.get(quality, 16000)
        self.audio_ctrl.set_sample_rate(target_sr)

        def _task():
            try:
                import time as _time
                self._processing_start = _time.time()
                
                # Reinicializar STTEngine si el modelo o dispositivo cambiaron
                if self.stt is None:
                    self._current_msg = _("⏳ Cargando modelo de IA...", self.lang)
                    self._queue.put(("PROGRESS", {"pct": 15, "msg": self._current_msg}))
                    
                    # Leer hilos desde config
                    th_str = self.cfg.get("threads", "Auto (predeterminado)")
                    th_map = { "2 hilos": 2, "4 hilos": 4, "8 hilos": 8 }
                    cpu_threads = th_map.get(th_str, 4)
                    
                    self.stt = STTEngine(model_size=stt_model, device=device, cpu_threads=cpu_threads)
                
                self._current_msg = _("🎙️ Transcribiendo audio...", self.lang)
                self._queue.put(("PROGRESS", {"pct": 30, "msg": self._current_msg}))
                # Nota: Pasamos el idioma si no es "auto"
                stt_lang = self.cfg.get("lang_stt", "auto")
                if "Español" in stt_lang: stt_lang = "es"
                elif "Inglés" in stt_lang: stt_lang = "en"
                else: stt_lang = None # auto detect

                result = self.stt.transcribe(file_path) # type: ignore
                
                self._current_msg = _("🔍 Analizando modismos...", self.lang)
                self._queue.put(("PROGRESS", {"pct": 70, "msg": self._current_msg}))
                processed_segments = []
                for seg in result.segmentos:
                    if auto_norm:
                        norm_seg, mod_seg = self.normalizer.normalize(seg.texto)
                    else:
                        norm_seg, mod_seg = seg.texto, []

                    processed_segments.append({
                        "start": seg.inicio,
                        "text": norm_seg,
                        "modismos": mod_seg
                    })
                
                self._current_msg = _("💾 Guardando resultados...", self.lang)
                self._queue.put(("PROGRESS", {"pct": 90, "msg": self._current_msg}))
                full_norm, all_mod = self.normalizer.normalize(result.texto_completo)
                acta = Acta(titulo=Path(file_path).stem, idioma=result.idioma_detectado,
                            duracion_segundos=int(result.duracion_procesada or 0), 
                            archivo_audio_ruta=file_path, modismos_detectados=all_mod,
                            transcripcion_texto=full_norm,
                            wer_medido=result.confianza_media)
                acta.version_diccionario = self.normalizer.version
                acta.id = self.db.insert_acta(acta)
                
                elapsed = int(_time.time() - self._processing_start)
                self._queue.put(("RESULT", {
                    "segments": processed_segments, 
                    "full_mods": all_mod, 
                    "elapsed": elapsed, 
                    "acta_id": acta.id
                }))
            except Exception as e:
                self._queue.put(("ERROR", {"msg": str(e)}))
        threading.Thread(target=_task, daemon=True).start()

    def _poll_queue(self):
        try:
            while True:
                msg_type, data = self._queue.get_nowait()
                tv = self.views["transcription"]
                
                if msg_type == "PROGRESS":
                    self._current_msg = data["msg"]
                    tv.progress_bar["value"] = data["pct"]
                    tv.progress_lbl.configure(text=f"{self._current_msg} (00:00)", fg=self.c["primary"])
                    
                elif msg_type == "RESULT":
                    self._is_processing = False
                    tv.txt.configure(state="normal")
                    tv.txt.delete("1.0", tk.END)
                    
                    for child in tv.mod_list.winfo_children():
                        child.destroy()
                    
                    for seg in data["segments"]:
                        tv.add_segment(seg["start"], seg["text"], seg["modismos"])
                    
                    for m in data["full_mods"]:
                        tv.add_modism_card(m.expresion_original, m.expresion_normalizada) # type: ignore
                    
                    elapsed = data.get("elapsed", 0)
                    tv.current_acta_id = data.get("acta_id")
                    tv.progress_bar["value"] = 100
                    
                    completed_msg = _("✓ Análisis completo — {segments} segmentos, {idioms} modismos detectados ({elapsed}s)", self.lang)
                    tv.progress_lbl.configure(
                        text=completed_msg.format(segments=len(data['segments']), idioms=len(data['full_mods']), elapsed=elapsed),
                        fg=self.c["success"]
                    )
                    tv.rec_btn.configure(text=_("⏺ Iniciar", self.lang), style="Primary.TButton", state="normal")
                    tv.cancel_btn.configure(text=_("🗑 Limpiar", self.lang), state="normal")
                    tv.btn_next.configure(state="normal")
                    
                elif msg_type == "ERROR":
                    self._is_processing = False
                    err_msg = data if isinstance(data, str) else data.get("msg", _("Error desconocido", self.lang))
                    error_tpl = _("❌ Error: {err_msg}", self.lang)
                    tv.progress_lbl.configure(text=error_tpl.format(err_msg=err_msg), fg=self.c.get("error", "#D32F2F"))
                    tv.progress_bar["value"] = 0
                    tv.rec_btn.configure(text=_("⏺ Iniciar", self.lang), style="Primary.TButton", state="normal")
                    messagebox.showerror(_("Error de IA", self.lang), str(err_msg))
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)
        
    def _setup_logging(self):
        """Configura el nivel de logging global según la configuración."""
        lvl_str = self.cfg.get("log_level", "Normal (predeterminado)")
        lvl_map = {
            "Solo errores": logging.ERROR,
            "Normal (predeterminado)": logging.INFO,
            "Detallado (debug)": logging.DEBUG
        }
        level = lvl_map.get(lvl_str, logging.INFO)
        
        # Configuración básica para el archivo de logs
        from src.config import USER_DATA_DIR
        import os
        log_dir = os.path.join(USER_DATA_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "actaclara.log")
        logging.basicConfig(
            filename=log_file,
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            encoding="utf-8"
        )

        # Limitar ruido de librerías externas
        logging.getLogger("faster_whisper").setLevel(logging.WARNING)
        logging.getLogger("ctranslate2").setLevel(logging.WARNING)
        
        logger.info(f"Logging inicializado en nivel: {lvl_str}")
        
    def _run_system_maintenance(self):
        """Ejecuta tareas de limpieza y respaldo automático según configuración."""
        if not self.cfg: return
        
        import datetime
        ahora = datetime.datetime.now()
        
        # 1. Limpieza automática de actas antiguas
        if self.cfg.get("auto_purge", False):
            # Mapear string a meses
            map_meses = { "1 mes": 1, "3 meses": 3, "6 meses": 6, "1 año": 12 }
            meses_str = self.cfg.get("purge_after", "6 meses")
            meses = map_meses.get(meses_str, 6)
            
            try:
                eliminadas = self.db.purge_old_actas(meses)
                if eliminadas > 0:
                    logging.info(f"Mantenimiento: Se eliminaron {eliminadas} actas antiguas automáticamente.")
            except Exception as e:
                logging.error(f"Error en purga automática: {e}")

        # 2. Respaldo automático
        if self.cfg.get("auto_backup", True):
            # Verificar frecuencia
            freq = self.cfg.get("backup_freq", "Semanal")
            dias_map = { "Diario": 1, "Semanal": 7, "Mensual": 30 }
            dias_umbral = dias_map.get(freq, 7)
            
            last_bk = self.cfg.get("last_backup_date", "")
            realizar_bk = False
            
            if not last_bk:
                realizar_bk = True
            else:
                try:
                    last_dt = datetime.datetime.fromisoformat(last_bk)
                    if (ahora - last_dt).days >= dias_umbral:
                        realizar_bk = True
                except:
                    realizar_bk = True
            
            if realizar_bk:
                logging.info(f"Iniciando respaldo automático (Frecuencia: {freq})")
                try:
                    # Ruta de la DB
                    from src.config import DB_PATH, USER_DATA_DIR
                    backups_dir = os.path.join(USER_DATA_DIR, "backups")
                    os.makedirs(backups_dir, exist_ok=True)
                    
                    ts = ahora.strftime("%d_%m_%Y__%H%M%S")
                    backup_name = f"auto_backup_{ts}"
                    backup_path = os.path.join(backups_dir, backup_name)
                    
                    import shutil
                    db_dir = os.path.dirname(DB_PATH)
                    shutil.make_archive(backup_path, 'zip', db_dir, os.path.basename(DB_PATH))
                    
                    # Actualizar fecha en config
                    self.cfg.set("last_backup_date", ahora.isoformat())
                    logging.info(f"Respaldo automático completado: {backup_name}.zip")
                except Exception as e:
                    logging.error(f"Fallo en respaldo automático: {e}")

    def on_closing(self):
        """Limpieza al cerrar la app."""
        self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
