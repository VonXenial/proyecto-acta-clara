🐍 ActaClara — Guía de implementación con Tkinter + ttk
1. Estructura de archivos recomendada
actaclara/
├── main.py                  # Punto de entrada
├── app.py                   # Clase principal App (ventana raíz)
├── styles.py                # Paleta de colores, fuentes y estilos ttk
├── views/
│   ├── __init__.py
│   ├── dashboard.py         # Pantalla Dashboard
│   ├── transcription.py     # Pantalla Transcripción en vivo
│   └── export.py            # Pantalla Exportación
├── components/
│   ├── __init__.py
│   ├── sidebar.py           # Barra lateral de navegación
│   ├── tooltip.py           # Widget Tooltip personalizado
│   └── modism_tag.py        # Etiqueta de modismo con tooltip
└── assets/
    └── icons/               # Íconos .png para botones (opcional)
2. Configuración de la ventana raíz (app.py)
# app.py
import tkinter as tk
from tkinter import ttk
from styles import apply_styles
from components.sidebar import Sidebar
from views.dashboard import DashboardView
from views.transcription import TranscriptionView
from views.export import ExportView

class ActaClaraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ── Ventana ──────────────────────────────────────────
        self.title("ActaClara")
        self.geometry("1366x768")
        self.resizable(False, False)
        self.configure(bg="#F5F7FA")

        # ── Estilos ttk globales ──────────────────────────────
        apply_styles(self)

        # ── Layout principal: sidebar + contenido ─────────────
        self.sidebar = Sidebar(self, on_navigate=self.show_view)
        self.sidebar.pack(side="left", fill="y")

        self.container = tk.Frame(self, bg="#F5F7FA")
        self.container.pack(side="left", fill="both", expand=True)

        # ── Registrar vistas ──────────────────────────────────
        self.views = {}
        for View in (DashboardView, TranscriptionView, ExportView):
            view = View(self.container)
            self.views[View.VIEW_NAME] = view
            view.place(relwidth=1, relheight=1)  # Apiladas, una sobre otra

        self.show_view("dashboard")

    def show_view(self, name: str):
        """Trae al frente la vista solicitada y actualiza el sidebar."""
        self.views[name].lift()
        self.sidebar.set_active(name)
3. Paleta de colores y estilos ttk (styles.py)
# styles.py
import tkinter as tk
from tkinter import ttk

# ── Paleta ────────────────────────────────────────────────────
COLORS = {
    "primary":      "#2E75B6",   # Azul corporativo
    "primary_dark": "#1F5280",
    "success":      "#28A745",   # Verde
    "warning":      "#FF8C00",   # Naranja
    "bg":           "#F5F7FA",   # Fondo general
    "sidebar_bg":   "#1E2A3A",   # Sidebar oscuro
    "sidebar_text": "#A8B8CC",
    "sidebar_active":"#2E75B6",
    "card_bg":      "#FFFFFF",
    "text_primary": "#1A2332",
    "text_secondary":"#6B7A8D",
    "border":       "#E1E8F0",
    "live_red":     "#DC3545",
}

# ── Fuentes ───────────────────────────────────────────────────
FONTS = {
    "title":   ("Segoe UI", 20, "bold"),
    "heading": ("Segoe UI", 13, "bold"),
    "body":    ("Segoe UI", 10),
    "small":   ("Segoe UI", 9),
    "mono":    ("Consolas", 10),
    "badge":   ("Segoe UI", 8, "bold"),
}

def apply_styles(root: tk.Tk):
    """Aplica el tema ttk global a la aplicación."""
    style = ttk.Style(root)
    style.theme_use("clam")          # Base más personalizable que 'default'

    # ── Botón primario ────────────────────────────────────────
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="white",
        font=FONTS["body"],
        padding=(16, 8),
        relief="flat",
        borderwidth=0,
    )
    style.map("Primary.TButton",
        background=[("active", COLORS["primary_dark"]),
                    ("pressed", COLORS["primary_dark"])],
        relief=[("pressed", "flat")],
    )

    # ── Botón secundario (outline) ────────────────────────────
    style.configure(
        "Secondary.TButton",
        background=COLORS["card_bg"],
        foreground=COLORS["primary"],
        font=FONTS["body"],
        padding=(12, 7),
        relief="solid",
        borderwidth=1,
    )
    style.map("Secondary.TButton",
        background=[("active", "#EBF3FB")],
    )

    # ── Botón de éxito ────────────────────────────────────────
    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground="white",
        font=FONTS["body"],
        padding=(16, 8),
        relief="flat",
        borderwidth=0,
    )
    style.map("Success.TButton",
        background=[("active", "#1E7E34")],
    )

    # ── Botón peligro / grabación ─────────────────────────────
    style.configure(
        "Danger.TButton",
        background=COLORS["live_red"],
        foreground="white",
        font=FONTS["body"],
        padding=(16, 8),
        relief="flat",
        borderwidth=0,
    )

    # ── Frame de tarjeta ──────────────────────────────────────
    style.configure(
        "Card.TFrame",
        background=COLORS["card_bg"],
        relief="flat",
    )

    # ── Etiquetas ─────────────────────────────────────────────
    style.configure("Title.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_primary"],
        font=FONTS["title"],
    )
    style.configure("Heading.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_primary"],
        font=FONTS["heading"],
    )
    style.configure("Body.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
    )
    style.configure("Muted.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_secondary"],
        font=FONTS["small"],
    )

    # ── Separador ─────────────────────────────────────────────
    style.configure("TSeparator", background=COLORS["border"])

    # ── Combobox ──────────────────────────────────────────────
    style.configure("TCombobox",
        font=FONTS["body"],
        fieldbackground="white",
        selectbackground=COLORS["primary"],
    )

    # ── Progressbar ──────────────────────────────────────────
    style.configure("Blue.Horizontal.TProgressbar",
        troughcolor=COLORS["border"],
        background=COLORS["primary"],
        thickness=8,
    )
    style.configure("Green.Horizontal.TProgressbar",
        troughcolor=COLORS["border"],
        background=COLORS["success"],
        thickness=8,
    )

    # ── Notebook (tabs) ───────────────────────────────────────
    style.configure("TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
    )
    style.configure("TNotebook.Tab",
        background=COLORS["border"],
        foreground=COLORS["text_secondary"],
        padding=(16, 8),
        font=FONTS["body"],
    )
    style.map("TNotebook.Tab",
        background=[("selected", COLORS["card_bg"])],
        foreground=[("selected", COLORS["primary"])],
    )
4. Sidebar de navegación (components/sidebar.py)
# components/sidebar.py
import tkinter as tk
from styles import COLORS, FONTS

NAV_ITEMS = [
    ("dashboard",     "📊", "Dashboard"),
    ("transcription", "🎙️", "Transcripción"),
    ("export",        "📤", "Exportación"),
]

class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent,
            bg=COLORS["sidebar_bg"],
            width=220,
        )
        self.pack_propagate(False)   # Respeta el ancho fijo
        self.on_navigate = on_navigate
        self._buttons = {}

        # ── Logo / título ──────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["sidebar_bg"], pady=24)
        header.pack(fill="x")

        tk.Label(header,
            text="ActaClara",
            bg=COLORS["sidebar_bg"],
            fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack()

        tk.Label(header,
            text="Transcripción inteligente",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["small"],
        ).pack()

        ttk_sep = tk.Frame(self, bg=COLORS["primary"], height=2)
        ttk_sep.pack(fill="x", padx=16)

        # ── Ítems de navegación ───────────────────────────────
        nav_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        nav_frame.pack(fill="x", pady=16)

        for key, icon, label in NAV_ITEMS:
            btn = NavButton(nav_frame,
                icon=icon, label=label,
                command=lambda k=key: self.on_navigate(k),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._buttons[key] = btn

        # ── Versión al fondo ──────────────────────────────────
        tk.Label(self,
            text="v1.0.0-beta",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["small"],
        ).pack(side="bottom", pady=16)

    def set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)


class NavButton(tk.Frame):
    """Botón de navegación sidebar con estado activo."""
    def __init__(self, parent, icon, label, command):
        super().__init__(parent, bg=COLORS["sidebar_bg"], cursor="hand2")
        self.command = command
        self._active = False

        self.indicator = tk.Frame(self, width=4,
            bg=COLORS["sidebar_bg"])
        self.indicator.pack(side="left", fill="y")

        self.inner = tk.Frame(self, bg=COLORS["sidebar_bg"],
            pady=10, padx=12)
        self.inner.pack(side="left", fill="both", expand=True)

        tk.Label(self.inner,
            text=f"{icon}  {label}",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["body"],
            anchor="w",
        ).pack(fill="x")

        # Bind clicks en todos los sub-widgets
        for w in (self, self.inner, *self.inner.winfo_children()):
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def set_active(self, active: bool):
        self._active = active
        color = COLORS["sidebar_active"] if active else COLORS["sidebar_bg"]
        fg    = "white"               if active else COLORS["sidebar_text"]
        self.indicator.configure(bg=COLORS["primary"] if active else COLORS["sidebar_bg"])
        self.inner.configure(bg=color)
        self.configure(bg=color)
        for child in self.inner.winfo_children():
            child.configure(bg=color, fg=fg)

    def _on_enter(self, _=None):
        if not self._active:
            self.inner.configure(bg="#253447")
            self.configure(bg="#253447")

    def _on_leave(self, _=None):
        if not self._active:
            self.inner.configure(bg=COLORS["sidebar_bg"])
            self.configure(bg=COLORS["sidebar_bg"])
5. Componente Tooltip (components/tooltip.py)
# components/tooltip.py
import tkinter as tk
from styles import COLORS, FONTS

class Tooltip:
    """
    Tooltip que aparece al hacer hover sobre un widget.
    Uso:
        Tooltip(widget, title="Jalar la cuerda",
                body="Equivalente formal: ejercer presión")
    """
    def __init__(self, widget, title: str, body: str = ""):
        self.widget = widget
        self.title  = title
        self.body   = body
        self.tw     = None

        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4

        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)   # Sin decoración
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.configure(bg=COLORS["text_primary"])

        # Contenido
        frame = tk.Frame(self.tw,
            bg=COLORS["text_primary"], padx=12, pady=8)
        frame.pack()

        if self.title:
            tk.Label(frame,
                text=self.title,
                bg=COLORS["text_primary"],
                fg="white",
                font=FONTS["badge"],
            ).pack(anchor="w")

        if self.body:
            tk.Label(frame,
                text=self.body,
                bg=COLORS["text_primary"],
                fg="#A8B8CC",
                font=FONTS["small"],
                wraplength=240,
                justify="left",
            ).pack(anchor="w", pady=(2, 0))

    def hide(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None
6. Vista Dashboard (views/dashboard.py)
# views/dashboard.py
import tkinter as tk
from tkinter import ttk
from styles import COLORS, FONTS

class DashboardView(tk.Frame):
    VIEW_NAME = "dashboard"

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._build()

    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg"], pady=24, padx=32)
        header.pack(fill="x")

        tk.Label(header,
            text="Dashboard",
            bg=COLORS["bg"], fg=COLORS["text_primary"],
            font=FONTS["title"],
        ).pack(side="left")

        ttk.Button(header,
            text="+ Nueva sesión",
            style="Primary.TButton",
        ).pack(side="right")

        # ── Tarjetas KPI ───────────────────────────────────────
        kpi_frame = tk.Frame(self, bg=COLORS["bg"], padx=32)
        kpi_frame.pack(fill="x")

        kpis = [
            ("12",  "Sesiones este mes",  COLORS["primary"]),
            ("94%", "Precisión promedio", COLORS["success"]),
            ("47",  "Modismos detectados",COLORS["warning"]),
            ("8.3h","Horas transcritas",  COLORS["primary"]),
        ]
        for col, (value, label, color) in enumerate(kpis):
            kpi_frame.columnconfigure(col, weight=1, uniform="kpi")
            card = self._kpi_card(kpi_frame, value, label, color)
            card.grid(row=0, column=col, padx=(0, 16) if col < 3 else 0, sticky="ew")

        # ── Historial reciente ─────────────────────────────────
        self._recent_section()

    def _kpi_card(self, parent, value, label, color):
        card = tk.Frame(parent,
            bg=COLORS["card_bg"],
            padx=24, pady=20,
        )
        # Borde izquierdo coloreado simulado con un Frame
        accent = tk.Frame(card, bg=color, width=4)
        accent.place(relheight=1, x=0, y=0)

        inner = tk.Frame(card, bg=COLORS["card_bg"], padx=12)
        inner.pack(fill="both", expand=True)

        tk.Label(inner,
            text=value,
            bg=COLORS["card_bg"], fg=color,
            font=("Segoe UI", 28, "bold"),
        ).pack(anchor="w")
        tk.Label(inner,
            text=label,
            bg=COLORS["card_bg"], fg=COLORS["text_secondary"],
            font=FONTS["small"],
        ).pack(anchor="w")
        return card

    def _recent_section(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=32, pady=24)
        frame.pack(fill="both", expand=True)

        tk.Label(frame,
            text="Sesiones recientes",
            bg=COLORS["bg"], fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 12))

        # Tabla con ttk.Treeview
        cols = ("Nombre", "Fecha", "Duración", "Modismos", "Precisión", "Estado")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=160 if col == "Nombre" else 110, anchor="center")

        rows = [
            ("Reunión Q1 2026",    "15/03/2026", "1h 23m", "12", "96%", "✅ Completado"),
            ("Kick-off Proyecto X","12/03/2026", "45m",    "8",  "94%", "✅ Completado"),
            ("Revisión mensual",   "08/03/2026", "2h 10m", "19", "91%", "✅ Completado"),
            ("Entrevista cliente", "05/03/2026", "30m",    "4",  "98%", "✅ Completado"),
        ]
        for row in rows:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
7. Vista Transcripción en vivo (views/transcription.py)
# views/transcription.py
import tkinter as tk
from tkinter import ttk
from styles import COLORS, FONTS
from components.tooltip import Tooltip

MODISMOS_DB = {
    "jalar la cuerda": "Ejercer presión para obtener un resultado",
    "quemar las naves": "Comprometerse sin posibilidad de retroceso",
    "meter el pie":     "Intervenir en un asunto ajeno",
    "dar en el clavo":  "Acertar completamente en algo",
}

class TranscriptionView(tk.Frame):
    VIEW_NAME = "transcription"

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._recording = False
        self._build()

    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg"], pady=20, padx=32)
        header.pack(fill="x")

        tk.Label(header,
            text="Transcripción en vivo",
            bg=COLORS["bg"], fg=COLORS["text_primary"],
            font=FONTS["title"],
        ).pack(side="left")

        # Indicador LIVE
        self.live_indicator = tk.Label(header,
            text="● EN VIVO",
            bg=COLORS["bg"], fg=COLORS["live_red"],
            font=FONTS["badge"],
        )
        self.live_indicator.pack(side="left", padx=16)
        self.live_indicator.pack_forget()    # Oculto hasta grabar

        # ── Controles de audio ────────────────────────────────
        ctrl = tk.Frame(self, bg=COLORS["card_bg"],
            padx=32, pady=16)
        ctrl.pack(fill="x", padx=32, pady=(0, 8))

        self.rec_btn = ttk.Button(ctrl,
            text="⏺  Iniciar grabación",
            style="Primary.TButton",
            command=self._toggle_recording,
        )
        self.rec_btn.pack(side="left", padx=(0, 12))

        ttk.Button(ctrl,
            text="⏸  Pausar",
            style="Secondary.TButton",
        ).pack(side="left", padx=(0, 12))

        # Selector de idioma / fuente
        tk.Label(ctrl,
            text="Idioma:",
            bg=COLORS["card_bg"], fg=COLORS["text_secondary"],
            font=FONTS["body"],
        ).pack(side="left", padx=(24, 4))

        lang_var = tk.StringVar(value="Español (MX)")
        ttk.Combobox(ctrl,
            textvariable=lang_var,
            values=["Español (MX)", "Español (ES)", "Inglés (US)"],
            width=16, state="readonly",
        ).pack(side="left")

        # ── Layout de dos columnas ────────────────────────────
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=32, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Área de transcripción
        self._build_transcript_area(body)

        # Panel lateral de modismos
        self._build_modisms_panel(body)

    def _build_transcript_area(self, parent):
        card = tk.Frame(parent,
            bg=COLORS["card_bg"],
            padx=24, pady=20,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(card,
            text="Transcripción",
            bg=COLORS["card_bg"], fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 8))

        # Text widget con scrollbar
        txt_frame = tk.Frame(card, bg=COLORS["border"], pady=1, padx=1)
        txt_frame.pack(fill="both", expand=True)

        self.txt = tk.Text(txt_frame,
            font=FONTS["body"],
            bg="white",
            fg=COLORS["text_primary"],
            relief="flat",
            wrap="word",
            padx=16, pady=12,
            spacing2=4,
        )
        # Tag para modismos detectados (resaltado naranja)
        self.txt.tag_configure("modismo",
            background="#FFF3E0",
            foreground=COLORS["warning"],
            underline=True,
        )
        sb = ttk.Scrollbar(txt_frame,
            command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt.pack(fill="both", expand=True)

        # Texto de ejemplo con modismo marcado
        sample = (
            "Gerente: Buenos días a todos. Necesitamos revisar el avance del "
            "proyecto antes de que el cliente meta el pie en el proceso…\n\n"
            "Analista: Entendido. El equipo ha dado en el clavo con la "
            "solución propuesta la semana pasada."
        )
        self.txt.insert("1.0", sample)
        # Resaltar modismos de ejemplo
        self._highlight_modismo("meta el pie")
        self._highlight_modismo("dado en el clavo")
        self.txt.configure(state="disabled")

    def _highlight_modismo(self, phrase: str):
        """Resalta todas las ocurrencias de un modismo en el Text widget."""
        start = "1.0"
        while True:
            pos = self.txt.search(phrase, start, stopindex="end",
                nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(phrase)}c"
            self.txt.tag_add("modismo", pos, end)
            start = end

    def _build_modisms_panel(self, parent):
        card = tk.Frame(parent,
            bg=COLORS["card_bg"],
            padx=20, pady=20,
        )
        card.grid(row=0, column=1, sticky="nsew")

        tk.Label(card,
            text="Modismos detectados",
            bg=COLORS["card_bg"], fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 12))

        detected = [
            ("meter el pie",    "Intervenir en asunto ajeno"),
            ("dar en el clavo", "Acertar completamente"),
        ]
        for modismo, equiv in detected:
            self._modismo_card(card, modismo, equiv)

    def _modismo_card(self, parent, modismo: str, equiv: str):
        card = tk.Frame(parent,
            bg="#FFF3E0",
            padx=12, pady=10,
        )
        card.pack(fill="x", pady=(0, 8))

        tk.Label(card,
            text=f'"{modismo}"',
            bg="#FFF3E0",
            fg=COLORS["warning"],
            font=FONTS["badge"],
        ).pack(anchor="w")

        tk.Label(card,
            text=f"→ {equiv}",
            bg="#FFF3E0",
            fg=COLORS["text_secondary"],
            font=FONTS["small"],
            wraplength=180,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        # Agregar tooltip al card
        Tooltip(card,
            title=f"Modismo: {modismo}",
            body=f"Significado: {equiv}",
        )

    def _toggle_recording(self):
        self._recording = not self._recording
        if self._recording:
            self.rec_btn.configure(
                text="⏹  Detener grabación",
                style="Danger.TButton",
            )
            self.live_indicator.pack(side="left", padx=16)
        else:
            self.rec_btn.configure(
                text="⏺  Iniciar grabación",
                style="Primary.TButton",
            )
            self.live_indicator.pack_forget()
8. Vista Exportación (views/export.py)
# views/export.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from styles import COLORS, FONTS

EXPORT_FORMATS = [
    ("PDF Formal",   "📄", "Documento con membrete corporativo", COLORS["primary"]),
    ("DOCX Word",    "📝", "Editable en Microsoft Word",         COLORS["primary"]),
    ("TXT Plano",    "🗒️", "Texto sin formato",                  COLORS["text_secondary"]),
    ("JSON Datos",   "⚙️", "Para integración con otros sistemas", COLORS["warning"]),
]

class ExportView(tk.Frame):
    VIEW_NAME = "export"

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._format_var = tk.StringVar(value="PDF Formal")
        self._normalize_var = tk.BooleanVar(value=True)
        self._timestamps_var = tk.BooleanVar(value=True)
        self._speakers_var   = tk.BooleanVar(value=True)
        self._build()

    def _build(self):
        # ── Encabezado ─────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg"], pady=20, padx=32)
        header.pack(fill="x")

        tk.Label(header,
            text="Exportar sesión",
            bg=COLORS["bg"], fg=COLORS["text_primary"],
            font=FONTS["title"],
        ).pack(side="left")

        # ── Cuerpo en dos columnas ────────────────────────────
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=32, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_format_selector(body)
        self._build_options_panel(body)

    def _build_format_selector(self, parent):
        card = tk.Frame(parent,
            bg=COLORS["card_bg"],
            padx=24, pady=24,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        tk.Label(card,
            text="Selecciona el formato de exportación",
            bg=COLORS["card_bg"], fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 16))

        for fmt_name, icon, desc, color in EXPORT_FORMATS:
            self._format_card(card, fmt_name, icon, desc, color)

        # Botón exportar
        ttk.Button(card,
            text="📥  Exportar ahora",
            style="Success.TButton",
            command=self._do_export,
        ).pack(anchor="w", pady=(20, 0))

    def _format_card(self, parent, name, icon, desc, color):
        is_selected = self._format_var.get() == name

        outer = tk.Frame(parent,
            bg=COLORS["primary"] if is_selected else COLORS["border"],
            pady=1, padx=1,
        )
        outer.pack(fill="x", pady=(0, 8))

        inner = tk.Frame(outer,
            bg="#EBF3FB" if is_selected else COLORS["card_bg"],
            padx=16, pady=14,
            cursor="hand2",
        )
        inner.pack(fill="both")

        tk.Label(inner,
            text=f"{icon}  {name}",
            bg=inner["bg"], fg=color,
            font=FONTS["heading"],
        ).pack(side="left")

        tk.Label(inner,
            text=desc,
            bg=inner["bg"], fg=COLORS["text_secondary"],
            font=FONTS["small"],
        ).pack(side="left", padx=12)

        # Radio button alineado a la derecha
        rb = tk.Radiobutton(inner,
            variable=self._format_var,
            value=name,
            bg=inner["bg"],
            activebackground=inner["bg"],
            command=self._rebuild_formats,
        )
        rb.pack(side="right")

        # Click en toda la tarjeta selecciona el radio
        for w in (inner, *inner.winfo_children()):
            w.bind("<Button-1>",
                lambda e, n=name: [self._format_var.set(n),
                                   self._rebuild_formats()])

    def _rebuild_formats(self):
        """Re-dibuja la columna izquierda para reflejar selección."""
        # Obtener el Frame padre de las tarjetas
        pass   # Simplificado: en producción, destruir y recrear tarjetas

    def _build_options_panel(self, parent):
        card = tk.Frame(parent,
            bg=COLORS["card_bg"],
            padx=24, pady=24,
        )
        card.grid(row=0, column=1, sticky="nsew")

        tk.Label(card,
            text="Opciones",
            bg=COLORS["card_bg"], fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 16))

        options = [
            (self._normalize_var, "Normalizar modismos",
             "Reemplaza expresiones coloquiales por lenguaje formal"),
            (self._timestamps_var, "Incluir marcas de tiempo",
             "Añade el minuto y segundo de cada intervención"),
            (self._speakers_var,  "Identificar hablantes",
             "Etiqueta cada segmento con el nombre del hablante"),
        ]
        for var, label, hint in options:
            self._option_row(card, var, label, hint)

        # Separador
        ttk.Separator(card, orient="horizontal").pack(
            fill="x", pady=16)

        # Vista previa de nombre de archivo
        tk.Label(card,
            text="Archivo de salida:",
            bg=COLORS["card_bg"], fg=COLORS["text_secondary"],
            font=FONTS["small"],
        ).pack(anchor="w")

        self.filename_lbl = tk.Label(card,
            text="reunion_q1_2026_normalizada.pdf",
            bg=COLORS["card_bg"], fg=COLORS["primary"],
            font=FONTS["mono"],
        )
        self.filename_lbl.pack(anchor="w", pady=(4, 0))

    def _option_row(self, parent, var, label, hint):
        row = tk.Frame(parent, bg=COLORS["card_bg"], pady=6)
        row.pack(fill="x")

        cb = ttk.Checkbutton(row,
            variable=var,
            text=label,
        )
        cb.pack(side="left")

        tk.Label(row,
            text="ℹ",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            cursor="question_arrow",
            font=("Segoe UI", 11),
        ).pack(side="left", padx=4)

        from components.tooltip import Tooltip
        Tooltip(row, title=label, body=hint)

    def _do_export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Texto", "*.txt"),
                ("JSON", "*.json"),
            ],
            title="Guardar transcripción",
        )
        if path:
            messagebox.showinfo(
                "Exportación completada",
                f"Archivo guardado en:\n{path}",
            )
9. Punto de entrada (main.py)
# main.py
from app import ActaClaraApp

if __name__ == "__main__":
    app = ActaClaraApp()
    app.mainloop()
Equivalencias clave React → Tkinter
Concepto React/CSS	Equivalente Tkinter
flex / grid layout	.pack(), .grid()
position: absolute	.place()
CSS variables / tokens	Diccionario COLORS en styles.py
Componente React	Clase que hereda de tk.Frame
useState	tk.StringVar, tk.BooleanVar, tk.IntVar
React Router	Método show_view() + .lift()
Tailwind clases	ttk.Style.configure() con nombres custom
onClick	.bind("<Button-1>", ...) o command=
onHover tooltip	Clase Tooltip con <Enter>/<Leave>
<select>	ttk.Combobox
<input type=checkbox>	ttk.Checkbutton
<progress>	ttk.Progressbar
<table>	ttk.Treeview
<textarea>	tk.Text
Text highlight (modismos)	tk.Text.tag_configure() + tag_add()
Notas importantes
Fuente Segoe UI: disponible nativamente en Windows. En macOS usa "SF Pro Display" y en Linux "DejaVu Sans" — detecta el SO con platform.system().
Resolución fija: self.geometry("1366x768") con resizable(False, False) replica exactamente el mockup desktop.
Borde izquierdo en tarjetas KPI: Tkinter no tiene border-left, se simula con un tk.Frame(width=4) de color + .place().
Refresh de formato seleccionado: implementa _rebuild_formats() destruyendo y recreando los widgets hijos del frame de formatos con for w in frame.winfo_children(): w.destroy().
Íconos: usa emojis Unicode directamente en text= para máxima portabilidad sin dependencias externas.