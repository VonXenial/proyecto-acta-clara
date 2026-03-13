"""
ActaClara – Main Window con Integración Lógica (P3 – Fase 2)
=============================================================
Conecta AudioController, STTEngine, Normalizer y DBManager
con la UI de Tkinter mediante un hilo de trabajo dedicado.

Flujo completo:
  1. Usuario elige archivo WAV/MP3 → filedialog
  2. AudioController.preprocess_for_whisper()  (hilo separado)
  3. STTEngine.transcribe()                    (hilo separado)
  4. Normalizer.normalize()                    (hilo separado)
  5. Resultado mostrado en TranscripcionView + modismos resaltados
  6. DBManager.insert_acta() guarda en SQLite  (hilo separado)
"""

# ── Codificación explícita para soportar emojis en Python estándar ────────────
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import logging
import threading
import tempfile
import queue
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ── Módulos del proyecto ──────────────────────────────────────────────────────
from src.controllers.audio_controller import AudioController
from src.services.stt_engine import STTEngine
from src.services.normalizer import Normalizer
from src.database.db_manager import DBManager
from src.models.acta import Acta
from src.models.modismo import ModismoDetectado

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/ui.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("MainWindow")


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  PALETA Y CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "primary":       "#2E75B6",
    "primary_dark":  "#1E5A96",
    "success":       "#28A745",
    "success_dark":  "#1C7A34",
    "warning":       "#FFC107",
    "danger":        "#DC3545",
    "highlight":     "#FFE0A0",   # Fondo naranja suave para modismos
    "bg_light":      "#F8F9FA",
    "bg_white":      "#FFFFFF",
    "border":        "#E0E0E0",
    "text_primary":  "#212529",
    "text_muted":    "#6C757D",
    "topbar_bg":     "#FFFFFF",
    "sidebar_bg":    "#F0F2F5",
}

FONT   = "Segoe UI"

# Tipos de mensaje que el hilo de trabajo envía al hilo de la UI
# (tipo, payload)
MSG_PROGRESS  = "progress"   # (paso_actual, total_pasos, mensaje)
MSG_RESULT    = "result"     # (texto_normalizado, modismos, acta_id)
MSG_ERROR     = "error"      # (mensaje_error,)
MSG_STATUS    = "status"     # (mensaje,)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  UTILIDADES DE WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

def _flat_btn(
    parent: tk.Widget,
    text: str,
    command: Callable = None,
    bg: str = COLORS["primary"],
    fg: str = "#FFF",
    font_size: int = 11,
    padx: int = 22,
    pady: int = 10,
    cursor: str = "hand2",
) -> tk.Button:
    """Botón plano (sin relieve 3-D) con efecto hover."""
    dark = _darken(bg)
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=dark, activeforeground=fg,
        font=(FONT, font_size, "bold"), padx=padx, pady=pady,
        relief=tk.FLAT, bd=0, cursor=cursor,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=dark))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def _darken(hex_color: str, factor: float = 0.82) -> str:
    """Oscurece un color hexadecimal."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
    except Exception:
        return hex_color


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  BARRA DE NAVEGACIÓN SUPERIOR
# ═══════════════════════════════════════════════════════════════════════════════

class TopBar(tk.Frame):
    NAV_ITEMS = [
        ("\U0001f3e0  Inicio",        "dashboard"),
        ("\U0001f4c4  Historial",     "historial"),
        ("\u2699\ufe0f  Configuraci\u00f3n", "config"),
        ("\u2753  Ayuda",             "ayuda"),
    ]

    def __init__(self, master: tk.Widget, on_navigate: Callable, **kwargs):
        super().__init__(
            master, bg=COLORS["topbar_bg"], height=60,
            highlightbackground=COLORS["border"], highlightthickness=1, **kwargs,
        )
        self.pack_propagate(False)
        self._active = "dashboard"
        self._btns: dict[str, tk.Button] = {}
        self._on_navigate = on_navigate
        self._build()

    def _build(self):
        logo = tk.Frame(self, bg=COLORS["topbar_bg"])
        logo.pack(side=tk.LEFT, padx=(20, 40))
        tk.Label(logo, text="\U0001f399\ufe0f", font=(FONT, 20), bg=COLORS["topbar_bg"],
                 fg=COLORS["primary"]).pack(side=tk.LEFT)
        tk.Label(logo, text="ActaClara", font=(FONT, 16, "bold"), bg=COLORS["topbar_bg"],
                 fg=COLORS["primary"]).pack(side=tk.LEFT, padx=(6, 0))

        tk.Frame(self, width=1, bg=COLORS["border"]).pack(side=tk.LEFT, fill=tk.Y, pady=10)

        nav = tk.Frame(self, bg=COLORS["topbar_bg"])
        nav.pack(side=tk.LEFT, padx=20)
        for label, vid in self.NAV_ITEMS:
            btn = tk.Button(
                nav, text=label, font=(FONT, 10),
                bg=COLORS["topbar_bg"], fg=COLORS["text_primary"],
                activebackground=COLORS["bg_light"], activeforeground=COLORS["primary"],
                relief=tk.FLAT, bd=0, padx=14, pady=18, cursor="hand2",
                command=lambda v=vid: self._nav(v),
            )
            btn.pack(side=tk.LEFT)
            self._btns[vid] = btn
        self._highlight()

    def _nav(self, vid: str):
        self._active = vid
        self._highlight()
        self._on_navigate(vid)

    def _highlight(self):
        for vid, btn in self._btns.items():
            if vid == self._active:
                btn.config(fg=COLORS["primary"], font=(FONT, 10, "bold"))
            else:
                btn.config(fg=COLORS["text_primary"], font=(FONT, 10))

    def set_active(self, vid: str):
        self._active = vid
        self._highlight()


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  PANEL LATERAL – HISTORIAL
# ═══════════════════════════════════════════════════════════════════════════════

class SidebarPanel(tk.Frame):
    def __init__(self, master: tk.Widget, **kwargs):
        super().__init__(
            master, bg=COLORS["sidebar_bg"], width=260,
            highlightbackground=COLORS["border"], highlightthickness=1, **kwargs,
        )
        self.pack_propagate(False)
        self._list_frame: Optional[tk.Frame] = None
        self._canvas: Optional[tk.Canvas] = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["sidebar_bg"])
        header.pack(fill=tk.X, padx=16, pady=(16, 8))
        tk.Label(header, text="\U0001f4cb  Historial", font=(FONT, 11, "bold"),
                 bg=COLORS["sidebar_bg"], fg=COLORS["text_primary"], anchor="w").pack(side=tk.LEFT)
        tk.Frame(self, height=1, bg=COLORS["border"]).pack(fill=tk.X)

        self._canvas = tk.Canvas(self, bg=COLORS["sidebar_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._list_frame = tk.Frame(self._canvas, bg=COLORS["sidebar_bg"])
        win = self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")

        self._list_frame.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(win, width=e.width))

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def add_entry(self, titulo: str, fecha: str):
        """Agrega una nueva entrada al historial (llamado desde el hilo UI)."""
        if self._list_frame is None:
            return
        self._add_item(self._list_frame, titulo, fecha)

    def _add_item(self, parent: tk.Frame, nombre: str, fecha: str):
        item = tk.Frame(parent, bg=COLORS["sidebar_bg"], cursor="hand2")
        item.pack(fill=tk.X, padx=8, pady=3)
        inner = tk.Frame(item, bg=COLORS["bg_white"], padx=10, pady=8,
                         highlightbackground=COLORS["border"], highlightthickness=1)
        inner.pack(fill=tk.X)
        tk.Label(inner, text="\U0001f4c4", font=(FONT, 14), bg=COLORS["bg_white"]
                 ).grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="ns")
        tk.Label(inner, text=nombre[:28], font=(FONT, 9, "bold"), bg=COLORS["bg_white"],
                 fg=COLORS["text_primary"], anchor="w", wraplength=160, justify=tk.LEFT
                 ).grid(row=0, column=1, sticky="w")
        tk.Label(inner, text=fecha, font=(FONT, 8), bg=COLORS["bg_white"],
                 fg=COLORS["text_muted"], anchor="w").grid(row=1, column=1, sticky="w")

        def on_enter(e):
            inner.config(bg=COLORS["bg_light"])
            for ch in inner.winfo_children():
                ch.config(bg=COLORS["bg_light"])

        def on_leave(e):
            inner.config(bg=COLORS["bg_white"])
            for ch in inner.winfo_children():
                ch.config(bg=COLORS["bg_white"])

        for w in [inner] + list(inner.winfo_children()):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  VISTA DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardView(tk.Frame):
    def __init__(self, master: tk.Widget,
                 on_new_acta: Callable,
                 on_import: Callable,
                 **kwargs):
        super().__init__(master, bg=COLORS["bg_white"], **kwargs)
        self._on_new_acta = on_new_acta
        self._on_import   = on_import
        self._build()

    def _build(self):
        tk.Frame(self, bg=COLORS["bg_white"]).pack(expand=True, fill=tk.BOTH)

        center = tk.Frame(self, bg=COLORS["bg_white"])
        center.pack()

        tk.Label(center, text="\U0001f399\ufe0f", font=(FONT, 56), bg=COLORS["bg_white"]
                 ).pack(pady=(0, 8))
        tk.Label(center, text="ActaClara", font=(FONT, 22, "bold"), bg=COLORS["bg_white"],
                 fg=COLORS["text_primary"]).pack()
        tk.Label(center, text="Transcripci\u00f3n y gesti\u00f3n de actas con IA",
                 font=(FONT, 11), bg=COLORS["bg_white"], fg=COLORS["text_muted"]
                 ).pack(pady=(4, 32))

        _flat_btn(center, text="\U0001f399\ufe0f   Nueva Acta",
                  command=self._on_new_acta, font_size=14, padx=40, pady=16
                  ).pack()

        tk.Label(center, text="Graba o importa audio para comenzar",
                 font=(FONT, 9), bg=COLORS["bg_white"], fg=COLORS["text_muted"]
                 ).pack(pady=(10, 0))

        quick = tk.Frame(self, bg=COLORS["bg_white"])
        quick.pack(pady=(40, 0))
        tk.Label(quick, text="\u2014 Acceso r\u00e1pido \u2014",
                 font=(FONT, 9), bg=COLORS["bg_white"], fg=COLORS["text_muted"]
                 ).pack(pady=(0, 12))

        row = tk.Frame(quick, bg=COLORS["bg_white"])
        row.pack()
        _flat_btn(row, "\U0001f4c1  Importar Audio",
                  command=self._on_import, font_size=9, padx=16, pady=8
                  ).pack(side=tk.LEFT, padx=6)
        _flat_btn(row, "\u2705  Exportar Acta",
                  bg=COLORS["success"], font_size=9, padx=16, pady=8
                  ).pack(side=tk.LEFT, padx=6)

        tk.Frame(self, bg=COLORS["bg_white"]).pack(expand=True, fill=tk.BOTH)


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  VISTA TRANSCRIPCIÓN (con highlighting de modismos)
# ═══════════════════════════════════════════════════════════════════════════════

class TranscripcionView(tk.Frame):
    """
    Editor de texto con:
      - Barra de herramientas (Guardar / Exportar)
      - Barra de progreso durante el procesamiento
      - Text widget con tag 'modismo' para resaltado naranja
    """

    def __init__(self, master: tk.Widget, **kwargs):
        super().__init__(master, bg=COLORS["bg_light"], **kwargs)
        self._text_widget: Optional[tk.Text] = None
        self._progress:    Optional[ttk.Progressbar] = None
        self._progress_lbl: Optional[tk.Label] = None
        self._build()

    # ── Construcción ──────────────────────────────────────────────────────────
    def _build(self):
        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48,
                           highlightbackground=COLORS["border"], highlightthickness=1)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="\U0001f4c4  Transcripci\u00f3n",
                 font=(FONT, 11, "bold"), bg=COLORS["topbar_bg"], fg=COLORS["text_primary"]
                 ).pack(side=tk.LEFT, padx=16)

        _flat_btn(toolbar, "\u2705  Exportar", bg=COLORS["success"],
                  font_size=9, padx=14, pady=6).pack(side=tk.RIGHT, padx=8, pady=8)
        _flat_btn(toolbar, "\U0001f4be  Guardar", bg=COLORS["primary"],
                  font_size=9, padx=14, pady=6).pack(side=tk.RIGHT, padx=(0, 4), pady=8)

        # Barra de progreso (oculta por defecto)
        prog_frame = tk.Frame(self, bg=COLORS["bg_light"], pady=4)
        prog_frame.pack(fill=tk.X, padx=20)

        self._progress_lbl = tk.Label(prog_frame, text="", font=(FONT, 8),
                                      bg=COLORS["bg_light"], fg=COLORS["text_muted"], anchor="w")
        self._progress_lbl.pack(side=tk.LEFT, padx=(0, 10))

        self._progress = ttk.Progressbar(prog_frame, mode="determinate",
                                         length=300, maximum=100)
        # No se hace `.pack()` hasta que sea necesario (se muestra/oculta dinámicamente)

        # Área de edición
        content = tk.Frame(self, bg=COLORS["bg_light"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 20))

        # Meta-datos
        self._meta_frame = tk.Frame(content, bg=COLORS["bg_white"], padx=20, pady=14,
                                    highlightbackground=COLORS["border"], highlightthickness=1)
        self._meta_frame.pack(fill=tk.X, pady=(0, 12))
        self._meta_labels: dict[str, tk.Label] = {}
        for i, (key, lbl, val) in enumerate([
            ("titulo",     "\U0001f4cc  T\u00edtulo:",       "—"),
            ("fecha",      "\U0001f4c5  Fecha:",             "—"),
            ("duracion",   "\u23f1\ufe0f  Duraci\u00f3n:",   "—"),
            ("idioma",     "\U0001f5fa\ufe0f  Idioma:",       "—"),
            ("modismos",   "\U0001f50d  Modismos:",          "—"),
        ]):
            tk.Label(self._meta_frame, text=lbl, font=(FONT, 9, "bold"),
                     bg=COLORS["bg_white"], fg=COLORS["text_muted"]
                     ).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=2)
            lbl_val = tk.Label(self._meta_frame, text=val, font=(FONT, 9),
                               bg=COLORS["bg_white"], fg=COLORS["text_primary"], anchor="w")
            lbl_val.grid(row=i, column=1, sticky="w", pady=2)
            self._meta_labels[key] = lbl_val

        # Editor
        editor = tk.Frame(content, bg=COLORS["bg_white"],
                          highlightbackground=COLORS["border"], highlightthickness=1)
        editor.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(editor)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._text_widget = tk.Text(
            editor, font=(FONT, 10), bg=COLORS["bg_white"], fg=COLORS["text_primary"],
            relief=tk.FLAT, padx=20, pady=16, wrap=tk.WORD,
            yscrollcommand=sb.set, insertbackground=COLORS["primary"],
        )
        self._text_widget.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._text_widget.yview)

        # Tag para resaltado de modismos
        self._text_widget.tag_configure(
            "modismo",
            background=COLORS["highlight"],
            foreground=COLORS["text_primary"],
        )
        self._text_widget.tag_configure(
            "modismo_hover",
            background=_darken(COLORS["highlight"], 0.9),
        )

        self._set_placeholder()

    # ── API pública ───────────────────────────────────────────────────────────

    def show_progress(self, value: float, message: str = ""):
        """Muestra y actualiza la barra de progreso (0–100)."""
        if not self._progress.winfo_ismapped():
            self._progress.pack(side=tk.LEFT)
        self._progress["value"] = value
        self._progress_lbl.config(text=message)

    def hide_progress(self):
        """Oculta la barra de progreso."""
        if self._progress.winfo_ismapped():
            self._progress.pack_forget()
        self._progress_lbl.config(text="")

    def show_result(self, texto: str, modismos: List[ModismoDetectado],
                    titulo: str, duracion: float, idioma: str):
        """Muestra el texto transcrito y resalta los modismos."""
        # Meta-datos
        self._meta_labels["titulo"].config(text=titulo)
        self._meta_labels["fecha"].config(text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        mins, secs = divmod(int(duracion), 60)
        self._meta_labels["duracion"].config(text=f"{mins}m {secs}s")
        self._meta_labels["idioma"].config(text=idioma)
        self._meta_labels["modismos"].config(
            text=f"{len(modismos)} detectado(s)" if modismos else "Ninguno")

        # Texto
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete("1.0", tk.END)
        self._text_widget.insert(tk.END, texto)

        # Resaltar modismos
        for mod in modismos:
            start_idx = f"1.0 + {mod.posicion_inicio} chars"
            end_idx   = f"1.0 + {mod.posicion_fin} chars"
            try:
                self._text_widget.tag_add("modismo", start_idx, end_idx)
            except Exception:
                pass  # posición fuera de rango ignorada

        self.hide_progress()

    def show_error(self, message: str):
        """Muestra un mensaje de error en el área de texto."""
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete("1.0", tk.END)
        self._text_widget.insert(tk.END, f"[ERROR]\n\n{message}")
        self._text_widget.config(state=tk.DISABLED)
        self.hide_progress()

    def _set_placeholder(self):
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.insert(
            tk.END,
            "Aqu\u00ed aparecer\u00e1 el texto transcrito.\n\n"
            "Usa el bot\u00f3n '🎙️ Nueva Acta' o '\U0001f4c1 Importar Audio' para comenzar.\n\n"
            "Los modismos detectados se resaltar\u00e1n en naranja.",
        )
        self._text_widget.config(state=tk.DISABLED)


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  VISTAS PLACEHOLDER
# ═══════════════════════════════════════════════════════════════════════════════

class _PlaceholderView(tk.Frame):
    def __init__(self, master, icon: str, titulo: str, **kwargs):
        super().__init__(master, bg=COLORS["bg_light"], **kwargs)
        tk.Label(self, text=icon, font=(FONT, 36), bg=COLORS["bg_light"]).pack(pady=(60, 8))
        tk.Label(self, text=titulo, font=(FONT, 16, "bold"),
                 bg=COLORS["bg_light"], fg=COLORS["text_primary"]).pack()
        tk.Label(self, text="(Vista en construcci\u00f3n)",
                 font=(FONT, 10), bg=COLORS["bg_light"], fg=COLORS["text_muted"]).pack(pady=4)


class HistorialView(_PlaceholderView):
    def __init__(self, m, **kw):
        super().__init__(m, "\U0001f4cb", "Historial de Actas", **kw)


class ConfigView(_PlaceholderView):
    def __init__(self, m, **kw):
        super().__init__(m, "\u2699\ufe0f", "Configuraci\u00f3n", **kw)


class AyudaView(_PlaceholderView):
    def __init__(self, m, **kw):
        super().__init__(m, "\u2753", "Ayuda", **kw)


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  HILO DE TRABAJO – Pipeline de transcripción
# ═══════════════════════════════════════════════════════════════════════════════

class TranscriptionWorker(threading.Thread):
    """
    Hilo de trabajo que ejecuta el pipeline completo:
      AudioController → STTEngine → Normalizer → DBManager

    Comunica progreso y resultados a la UI mediante una Queue.
    """

    STEPS_TOTAL = 4

    def __init__(
        self,
        file_path: str,
        q: queue.Queue,
        audio_ctrl: AudioController,
        stt_engine: STTEngine,
        normalizer: Normalizer,
        db_manager: DBManager,
    ):
        super().__init__(daemon=True, name="TranscriptionWorker")
        self.file_path   = file_path
        self.q           = q
        self.audio_ctrl  = audio_ctrl
        self.stt_engine  = stt_engine
        self.normalizer  = normalizer
        self.db_manager  = db_manager

    # ── Helpers de comunicación ───────────────────────────────────────────────
    def _progress(self, step: int, msg: str):
        pct = int(step / self.STEPS_TOTAL * 100)
        self.q.put((MSG_PROGRESS, (pct, msg)))

    def _status(self, msg: str):
        self.q.put((MSG_STATUS, (msg,)))

    # ── Lógica principal ──────────────────────────────────────────────────────
    def run(self):
        tmp_wav = None
        try:
            # PASO 1 – Preprocesar audio
            self._progress(1, "Preprocesando audio…")
            logger.info(f"Worker: cargando audio desde '{self.file_path}'")
            audio_seg = self.audio_ctrl.load_audio(self.file_path)

            # Exportar a WAV temporal para Whisper
            tmp_dir = tempfile.mkdtemp()
            tmp_wav = os.path.join(tmp_dir, "audio_processed.wav")
            self.audio_ctrl.preprocess_for_whisper(audio_seg, tmp_wav)
            duracion_seg = len(audio_seg) / 1000.0  # pydub trabaja en ms

            # PASO 2 – Transcribir con Whisper
            self._progress(2, "Transcribiendo con Whisper…")
            logger.info("Worker: iniciando STTEngine.transcribe()")
            transcription = self.stt_engine.transcribe(tmp_wav)
            raw_text  = transcription.texto_completo
            idioma    = transcription.idioma_detectado or "es"

            # PASO 3 – Normalizar modismos
            self._progress(3, "Normalizando modismos…")
            logger.info("Worker: normalizando modismos")
            normalized_text, modismos = self.normalizer.normalize(raw_text)
            logger.info(f"Worker: {len(modismos)} modismo(s) detectados")

            # PASO 4 – Guardar en base de datos
            self._progress(4, "Guardando en base de datos…")
            titulo = Path(self.file_path).stem.replace("_", " ").title()
            acta = Acta(
                titulo=titulo,
                idioma=idioma,
                duracion_segundos=int(duracion_seg),
                archivo_audio_ruta=self.file_path,
                modismos_detectados=modismos if modismos else None,
            )
            acta_id = self.db_manager.insert_acta(acta)
            logger.info(f"Worker: acta guardada con ID {acta_id}")

            # Enviar resultado
            self.q.put((MSG_RESULT, {
                "texto":     normalized_text,
                "modismos":  modismos,
                "titulo":    titulo,
                "duracion":  duracion_seg,
                "idioma":    idioma,
                "acta_id":   acta_id,
            }))

        except Exception as exc:
            logger.exception(f"Worker: error en pipeline → {exc}")
            self.q.put((MSG_ERROR, (str(exc),)))

        finally:
            # Limpiar WAV temporal
            if tmp_wav and os.path.exists(tmp_wav):
                try:
                    os.remove(tmp_wav)
                except OSError:
                    pass


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(tk.Tk):
    """
    Ventana principal de ActaClara (1280×800 px).

    Coordina:
      - Navegación entre vistas
      - Apertura de diálogo de selección de archivo
      - Lanzamiento del hilo de transcripción
      - Polling de la Queue para actualizar la UI
      - Integración con los módulos del backend
    """

    def __init__(self):
        super().__init__()
        self.title("ActaClara \u2013 Gesti\u00f3n de Actas con IA")
        self.geometry("1280x800")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg_white"])

        # ── Cola de mensajes del hilo de trabajo ──────────────────────────────
        self._queue: queue.Queue = queue.Queue()
        self._worker_running = False

        # ── Backend (lazy-initialized para evitar cuelgues al arrancar) ───────
        self._audio_ctrl: Optional[AudioController] = None
        self._stt_engine: Optional[STTEngine]       = None
        self._normalizer: Optional[Normalizer]      = None
        self._db_manager: Optional[DBManager]       = None

        # ── UI ────────────────────────────────────────────────────────────────
        self._setup_style()
        self._build_layout()
        self._navigate("dashboard")

        # ── Inicializar backend en hilo separado ──────────────────────────────
        threading.Thread(target=self._init_backend, daemon=True,
                         name="BackendInit").start()

        # ── Arrancar polling de la cola ───────────────────────────────────────
        self._poll_queue()

    # ── Estilos ttk ───────────────────────────────────────────────────────────
    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TScrollbar", gripcount=0,
                         background=COLORS["border"], troughcolor=COLORS["bg_light"],
                         bordercolor=COLORS["bg_light"], arrowcolor=COLORS["text_muted"],
                         relief=tk.FLAT)
        style.configure("TProgressbar", troughcolor=COLORS["bg_light"],
                         background=COLORS["primary"], thickness=6)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self._topbar = TopBar(self, on_navigate=self._navigate)
        self._topbar.pack(side=tk.TOP, fill=tk.X)

        # Barra de estado inferior
        self._statusbar = tk.Frame(self, bg=COLORS["border"], height=24,
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1)
        self._statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._statusbar.pack_propagate(False)
        self._status_lbl = tk.Label(
            self._statusbar, text="  \u2713 Sistema listo",
            font=(FONT, 8), bg=COLORS["border"], fg=COLORS["text_muted"], anchor="w",
        )
        self._status_lbl.pack(side=tk.LEFT, padx=8)
        self._worker_lbl = tk.Label(
            self._statusbar, text="",
            font=(FONT, 8), bg=COLORS["border"], fg=COLORS["primary"], anchor="e",
        )
        self._worker_lbl.pack(side=tk.RIGHT, padx=8)

        body = tk.Frame(self, bg=COLORS["bg_white"])
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._sidebar = SidebarPanel(body)
        self._sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Frame(body, width=1, bg=COLORS["border"]).pack(side=tk.RIGHT, fill=tk.Y)

        self._center = tk.Frame(body, bg=COLORS["bg_white"])
        self._center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._views: dict[str, Optional[tk.Frame]] = {
            "dashboard":     None,
            "historial":     None,
            "transcripcion": None,
            "config":        None,
            "ayuda":         None,
        }
        self._current_view: Optional[tk.Frame] = None

    # ── Navegación ────────────────────────────────────────────────────────────
    def _navigate(self, vid: str):
        if self._current_view is not None:
            self._current_view.pack_forget()
        if self._views.get(vid) is None:
            self._views[vid] = self._create_view(vid)
        self._current_view = self._views[vid]
        self._current_view.pack(fill=tk.BOTH, expand=True)
        self._topbar.set_active(vid)

    def _create_view(self, vid: str) -> tk.Frame:
        c = self._center
        if vid == "dashboard":
            return DashboardView(c,
                                 on_new_acta=self._open_file_dialog,
                                 on_import=self._open_file_dialog)
        if vid == "historial":     return HistorialView(c)
        if vid == "transcripcion": return TranscripcionView(c)
        if vid == "config":        return ConfigView(c)
        if vid == "ayuda":         return AyudaView(c)
        ph = tk.Frame(c, bg=COLORS["bg_light"])
        tk.Label(ph, text=f"Vista '{vid}' no implementada",
                 font=(FONT, 12), fg=COLORS["text_muted"],
                 bg=COLORS["bg_light"]).pack(expand=True)
        return ph

    # ── Inicialización del backend ─────────────────────────────────────────────
    def _init_backend(self):
        """Se ejecuta en un hilo daemon al arrancar la app."""
        try:
            self._set_status("Inicializando AudioController…")
            self._audio_ctrl = AudioController()

            self._set_status("Cargando modelo Whisper (puede tardar)…")
            self._stt_engine = STTEngine()

            self._set_status("Cargando diccionario de modismos…")
            self._normalizer = Normalizer()

            self._set_status("Conectando a la base de datos…")
            self._db_manager = DBManager()
            self._db_manager.initialize_db()

            self._set_status("\u2713 Sistema listo")
            logger.info("Backend inicializado correctamente")
        except Exception as exc:
            logger.exception(f"Error al inicializar backend: {exc}")
            self._set_status(f"\u26a0 Error de inicio: {exc}")

    # ── Diálogo para seleccionar archivo ──────────────────────────────────────
    def _open_file_dialog(self):
        if self._worker_running:
            messagebox.showwarning(
                "Proceso en curso",
                "Hay una transcripci\u00f3n en curso. Por favor espera a que termine.",
                parent=self,
            )
            return

        if self._stt_engine is None:
            messagebox.showinfo(
                "Sistema iniciando",
                "El modelo de IA se est\u00e1 cargando. Por favor espera unos segundos e int\u00e9ntalo de nuevo.",
                parent=self,
            )
            return

        file_path = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.wav *.mp3 *.m4a *.ogg *.flac"),
                ("WAV", "*.wav"),
                ("MP3", "*.mp3"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if file_path:
            self._start_transcription(file_path)

    # ── Inicio de la transcripción en hilo separado ───────────────────────────
    def _start_transcription(self, file_path: str):
        """
        Lanza el hilo de transcripción y navega a la vista de transcripción.
        Mantiene la UI 100 % responsiva durante el proceso.
        """
        self._navigate("transcripcion")
        tv: TranscripcionView = self._views["transcripcion"]
        tv.show_progress(5, "Iniciando pipeline…")
        self._worker_running = True
        self._worker_lbl.config(text="\U0001f504 Procesando…")
        self._set_status(f"Procesando: {Path(file_path).name}")

        worker = TranscriptionWorker(
            file_path=file_path,
            q=self._queue,
            audio_ctrl=self._audio_ctrl,
            stt_engine=self._stt_engine,
            normalizer=self._normalizer,
            db_manager=self._db_manager,
        )
        worker.start()
        logger.info(f"Hilo de transcripción lanzado para: {file_path}")

    # ── Polling de la queue (ejecutado en el hilo de la UI) ───────────────────
    def _poll_queue(self):
        """Revisa la cola cada 100 ms y actualiza la UI según mensajes del worker."""
        try:
            while True:
                msg_type, payload = self._queue.get_nowait()
                self._handle_message(msg_type, payload)
        except queue.Empty:
            pass
        finally:
            # Re-programar en 100ms
            self.after(100, self._poll_queue)

    def _handle_message(self, msg_type: str, payload):
        tv: Optional[TranscripcionView] = self._views.get("transcripcion")  # type: ignore

        if msg_type == MSG_PROGRESS:
            pct, msg = payload
            self._set_status(msg)
            if tv:
                tv.show_progress(pct, msg)

        elif msg_type == MSG_STATUS:
            self._set_status(payload[0])

        elif msg_type == MSG_RESULT:
            self._worker_running = False
            self._worker_lbl.config(text="\u2705 Completado")
            titulo   = payload["titulo"]
            duracion = payload["duracion"]
            idioma   = payload["idioma"]

            if tv:
                tv.show_result(
                    texto    = payload["texto"],
                    modismos = payload["modismos"],
                    titulo   = titulo,
                    duracion = duracion,
                    idioma   = idioma,
                )

            # Actualizar sidebar
            fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._sidebar.add_entry(titulo, fecha_str)
            self._set_status(f"\u2713 Acta '{titulo}' guardada (ID {payload['acta_id']})")
            logger.info(f"UI actualizada con resultado del acta '{titulo}'")

        elif msg_type == MSG_ERROR:
            self._worker_running = False
            self._worker_lbl.config(text="\u26a0 Error")
            msg = payload[0]
            if tv:
                tv.show_error(msg)
            self._set_status(f"\u26a0 Error: {msg}")
            messagebox.showerror("Error de transcripci\u00f3n",
                                 f"No se pudo completar el proceso:\n\n{msg}", parent=self)

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _set_status(self, msg: str):
        """Actualiza la barra de estado inferior (thread-safe vía after)."""
        self.after(0, lambda: self._status_lbl.config(text=f"  {msg}"))

    # ── API pública ────────────────────────────────────────────────────────────
    def show_dashboard(self):    self._navigate("dashboard")
    def show_transcripcion(self): self._navigate("transcripcion")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Configurar logging básico para la consola cuando se ejecuta directamente
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    app = MainWindow()
    app.mainloop()
