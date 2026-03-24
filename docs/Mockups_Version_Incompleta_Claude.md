# 06 - INTERFAZ TKINTER: ESPECIFICACIONES COMPLETAS

**Documento:** P3 - Interfaz de Usuario con Tkinter + ttk  
**Versión:** 2.0  
**Fecha:** 14 marzo 2026  
**Para Agente:** A4 (UI Specialist - Claude Sonnet 4.6)  
**Basado en:** Mockups de Figma + Código generado por Figma

---

## 📋 ÍNDICE

1. [Arquitectura de la Aplicación](#arquitectura)
2. [Paleta de Colores y Estilos](#paleta-de-colores)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Ventana Principal](#ventana-principal)
5. [Componentes Reutilizables](#componentes-reutilizables)
6. [Pantalla 1: Dashboard](#pantalla-1-dashboard)
7. [Pantalla 2: Transcripción en Vivo](#pantalla-2-transcripción)
8. [Pantalla 3: Exportación](#pantalla-3-exportación)
9. [Integración con Backend](#integración-backend)
10. [Testing y Validación](#testing)

---

## 🏗️ ARQUITECTURA DE LA APLICACIÓN

### Patrón de Diseño

```
┌─────────────────────────────────────────────────────────┐
│                  ActaClaraApp (tk.Tk)                   │
│  - Ventana raíz única                                   │
│  - Gestión de navegación entre vistas                   │
│  - Configuración de estilos globales ttk                │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┬────────────┬──────────┐
       │                │            │          │
   ┌───▼───┐      ┌─────▼─────┐ ┌───▼───┐  ┌───▼───┐
   │Sidebar│      │ Dashboard │ │ Trans │  │Export │
   │       │      │   View    │ │ View  │  │ View  │
   └───────┘      └───────────┘ └───────┘  └───────┘
       │
   ┌───▼────────────┐
   │  NavButton (3) │
   └────────────────┘
```

### Flujo de Navegación

```python
# Usuario hace click en Sidebar
NavButton("Transcripción") → on_navigate("transcription")
                           → app.show_view("transcription")
                           → TranscriptionView.lift()
```

---

## 🎨 PALETA DE COLORES Y ESTILOS

### Archivo: `src/ui/styles.py`

```python
"""
Estilos globales de ActaClara
Paleta de colores corporativa y configuración de ttk
"""

import tkinter as tk
from tkinter import ttk

# ═══════════════════════════════════════════════════════
# PALETA DE COLORES
# ═══════════════════════════════════════════════════════

COLORS = {
    # Colores primarios
    "primary":          "#2E75B6",   # Azul corporativo (botones, enlaces)
    "primary_dark":     "#1F5280",   # Azul oscuro (hover, pressed)
    "primary_light":    "#EBF3FB",   # Azul claro (backgrounds, hover)
    
    # Colores de estado
    "success":          "#28A745",   # Verde (confirmaciones, éxito)
    "success_dark":     "#1E7E34",   # Verde oscuro (hover)
    "warning":          "#FF8C00",   # Naranja (modismos, advertencias)
    "warning_light":    "#FFF3E0",   # Naranja claro (backgrounds)
    "danger":           "#DC3545",   # Rojo (errores, grabación)
    "danger_dark":      "#A71D2A",   # Rojo oscuro (hover)
    
    # Fondos y contenedores
    "bg":               "#F5F7FA",   # Fondo general de la app
    "card_bg":          "#FFFFFF",   # Fondo de tarjetas/cards
    "sidebar_bg":       "#1E2A3A",   # Fondo del sidebar
    "sidebar_hover":    "#253447",   # Hover en items del sidebar
    "sidebar_active":   "#2E75B6",   # Item activo en sidebar
    
    # Textos
    "text_primary":     "#1A2332",   # Texto principal (títulos, body)
    "text_secondary":   "#6B7A8D",   # Texto secundario (hints, labels)
    "text_disabled":    "#A8B8CC",   # Texto deshabilitado
    "sidebar_text":     "#A8B8CC",   # Texto en sidebar (inactivo)
    "sidebar_text_active": "#FFFFFF", # Texto en sidebar (activo)
    
    # Bordes y separadores
    "border":           "#E1E8F0",   # Bordes sutiles
    "border_dark":      "#CBD5E0",   # Bordes más prominentes
    
    # Estados especiales
    "live_red":         "#DC3545",   # Indicador "EN VIVO"
    "badge_green":      "#28A745",   # Badge "Procesada"
    "badge_orange":     "#FF8C00",   # Badge "En edición"
}

# ═══════════════════════════════════════════════════════
# TIPOGRAFÍA
# ═══════════════════════════════════════════════════════

FONTS = {
    "title":    ("Segoe UI", 20, "bold"),    # Títulos de pantalla
    "heading":  ("Segoe UI", 13, "bold"),    # Subtítulos, secciones
    "body":     ("Segoe UI", 10),            # Texto normal
    "small":    ("Segoe UI", 9),             # Texto pequeño, hints
    "mono":     ("Consolas", 10),            # Código, rutas de archivo
    "badge":    ("Segoe UI", 8, "bold"),     # Badges, etiquetas
}

# ═══════════════════════════════════════════════════════
# DIMENSIONES
# ═══════════════════════════════════════════════════════

DIMENSIONS = {
    "window_width":     1366,
    "window_height":    768,
    "sidebar_width":    220,
    "padding_large":    32,
    "padding_medium":   20,
    "padding_small":    12,
    "padding_tiny":     8,
    "border_radius":    8,   # Nota: Tkinter no soporta border-radius nativamente
}

# ═══════════════════════════════════════════════════════
# CONFIGURACIÓN DE ESTILOS TTK
# ═══════════════════════════════════════════════════════

def apply_styles(root: tk.Tk):
    """
    Aplica estilos globales ttk a la aplicación.
    
    Args:
        root: Ventana raíz de Tkinter
    """
    style = ttk.Style(root)
    style.theme_use("clam")  # Base más personalizable
    
    # ─────────────────────────────────────────────────────
    # BOTONES
    # ─────────────────────────────────────────────────────
    
    # Botón primario (azul)
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
        background=[
            ("active", COLORS["primary_dark"]),
            ("pressed", COLORS["primary_dark"]),
            ("disabled", COLORS["border"])
        ],
        foreground=[("disabled", COLORS["text_disabled"])],
    )
    
    # Botón secundario (outline)
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
        background=[("active", COLORS["primary_light"])],
    )
    
    # Botón de éxito (verde)
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
        background=[
            ("active", COLORS["success_dark"]),
            ("disabled", COLORS["border"])
        ],
    )
    
    # Botón peligro (rojo) - para grabación
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="white",
        font=FONTS["body"],
        padding=(16, 8),
        relief="flat",
        borderwidth=0,
    )
    style.map("Danger.TButton",
        background=[("active", COLORS["danger_dark"])],
    )
    
    # ─────────────────────────────────────────────────────
    # FRAMES
    # ─────────────────────────────────────────────────────
    
    style.configure(
        "Card.TFrame",
        background=COLORS["card_bg"],
        relief="flat",
    )
    
    # ─────────────────────────────────────────────────────
    # LABELS
    # ─────────────────────────────────────────────────────
    
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
    
    # ─────────────────────────────────────────────────────
    # SEPARADORES
    # ─────────────────────────────────────────────────────
    
    style.configure("TSeparator",
        background=COLORS["border"]
    )
    
    # ─────────────────────────────────────────────────────
    # COMBOBOX
    # ─────────────────────────────────────────────────────
    
    style.configure("TCombobox",
        font=FONTS["body"],
        fieldbackground="white",
        selectbackground=COLORS["primary"],
    )
    
    # ─────────────────────────────────────────────────────
    # PROGRESSBAR
    # ─────────────────────────────────────────────────────
    
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
    
    # ─────────────────────────────────────────────────────
    # CHECKBUTTON
    # ─────────────────────────────────────────────────────
    
    style.configure("TCheckbutton",
        background=COLORS["card_bg"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
    )
    
    # ─────────────────────────────────────────────────────
    # RADIOBUTTON
    # ─────────────────────────────────────────────────────
    
    style.configure("TRadiobutton",
        background=COLORS["card_bg"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
    )
    
    # ─────────────────────────────────────────────────────
    # ENTRY
    # ─────────────────────────────────────────────────────
    
    style.configure("TEntry",
        font=FONTS["body"],
        fieldbackground="white",
        borderwidth=1,
    )
```

---

## 📁 ESTRUCTURA DE CARPETAS

```
ActaClara/
├── src/
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py                    # Ventana principal
│   │   ├── styles.py                 # Estilos y paleta de colores
│   │   │
│   │   ├── components/               # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py            # Barra lateral de navegación
│   │   │   ├── tooltip.py            # Tooltip emergente
│   │   │   ├── modism_tag.py         # Etiqueta de modismo con tooltip
│   │   │   ├── audio_timeline.py     # Timeline de audio
│   │   │   └── card.py               # Card genérico
│   │   │
│   │   └── views/                    # Pantallas principales
│   │       ├── __init__.py
│   │       ├── dashboard.py          # Vista Dashboard
│   │       ├── transcription.py      # Vista Transcripción
│   │       └── export.py             # Vista Exportación
│   │
│   ├── services/                     # Backend (ya existente)
│   ├── controllers/
│   ├── models/
│   └── database/
│
└── main.py                           # Punto de entrada
```

---

## 🪟 VENTANA PRINCIPAL

### Archivo: `src/ui/app.py`

```python
"""
Ventana principal de ActaClara
Gestiona navegación entre vistas y configuración global
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import apply_styles, COLORS, DIMENSIONS
from ui.components.sidebar import Sidebar
from ui.views.dashboard import DashboardView
from ui.views.transcription import TranscriptionView
from ui.views.export import ExportView


class ActaClaraApp(tk.Tk):
    """Aplicación principal de ActaClara."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        
        # ── Configuración de ventana ──────────────────────
        self.title("ActaClara - Transcripción Inteligente")
        self.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.resizable(False, False)  # Ventana de tamaño fijo
        self.configure(bg=COLORS["bg"])
        
        # ── Aplicar estilos ttk globales ──────────────────
        apply_styles(self)
        
        # ── Layout principal: Sidebar + Contenido ─────────
        self._setup_layout()
        
        # ── Registrar vistas ──────────────────────────────
        self._register_views()
        
        # ── Mostrar vista inicial ─────────────────────────
        self.show_view("dashboard")
    
    def _setup_layout(self):
        """Configura el layout principal de la aplicación."""
        # Sidebar (barra lateral izquierda)
        self.sidebar = Sidebar(self, on_navigate=self.show_view)
        self.sidebar.pack(side="left", fill="y")
        
        # Container para vistas (área principal)
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(side="left", fill="both", expand=True)
    
    def _register_views(self):
        """Registra todas las vistas de la aplicación."""
        self.views = {}
        
        # Crear instancias de cada vista
        for ViewClass in (DashboardView, TranscriptionView, ExportView):
            view = ViewClass(self.container)
            self.views[ViewClass.VIEW_NAME] = view
            
            # Apilar todas las vistas en el mismo espacio
            # (usando place para superposición)
            view.place(relwidth=1, relheight=1)
    
    def show_view(self, view_name: str):
        """
        Muestra la vista solicitada y la trae al frente.
        
        Args:
            view_name: Nombre de la vista ("dashboard", "transcription", "export")
        """
        if view_name in self.views:
            # Traer vista al frente
            self.views[view_name].lift()
            
            # Actualizar sidebar para reflejar vista activa
            self.sidebar.set_active(view_name)


def main():
    """Punto de entrada de la aplicación."""
    app = ActaClaraApp()
    app.mainloop()


if __name__ == "__main__":
    main()
```

---

## 🧩 COMPONENTES REUTILIZABLES

### 1. Sidebar (Barra Lateral)

**Archivo:** `src/ui/components/sidebar.py`

```python
"""
Sidebar de navegación con items clickeables
"""

import tkinter as tk
from ui.styles import COLORS, FONTS


# Definición de items de navegación
NAV_ITEMS = [
    ("dashboard",     "📊", "Dashboard"),
    ("transcription", "🎙️", "Transcripción"),
    ("export",        "📤", "Exportación"),
]


class Sidebar(tk.Frame):
    """Barra lateral de navegación."""
    
    def __init__(self, parent, on_navigate):
        """
        Inicializa el sidebar.
        
        Args:
            parent: Widget padre
            on_navigate: Callback cuando se hace click en un item
        """
        super().__init__(
            parent,
            bg=COLORS["sidebar_bg"],
            width=220,
        )
        
        self.pack_propagate(False)  # Mantener ancho fijo
        self.on_navigate = on_navigate
        self._buttons = {}
        
        self._build_header()
        self._build_navigation()
        self._build_footer()
    
    def _build_header(self):
        """Construye el header del sidebar (logo + título)."""
        header = tk.Frame(self, bg=COLORS["sidebar_bg"], pady=24)
        header.pack(fill="x")
        
        # Logo/Título
        tk.Label(
            header,
            text="ActaClara",
            bg=COLORS["sidebar_bg"],
            fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack()
        
        # Subtítulo
        tk.Label(
            header,
            text="Transcripción inteligente",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["small"],
        ).pack()
        
        # Separador
        tk.Frame(
            self,
            bg=COLORS["primary"],
            height=2
        ).pack(fill="x", padx=16)
    
    def _build_navigation(self):
        """Construye los items de navegación."""
        nav_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        nav_frame.pack(fill="x", pady=16)
        
        for key, icon, label in NAV_ITEMS:
            btn = NavButton(
                nav_frame,
                icon=icon,
                label=label,
                command=lambda k=key: self.on_navigate(k),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._buttons[key] = btn
    
    def _build_footer(self):
        """Construye el footer del sidebar (versión)."""
        tk.Label(
            self,
            text="v0.4",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["small"],
        ).pack(side="bottom", pady=16)
    
    def set_active(self, key: str):
        """
        Marca un item como activo.
        
        Args:
            key: Key del item a marcar como activo
        """
        for k, btn in self._buttons.items():
            btn.set_active(k == key)


class NavButton(tk.Frame):
    """Botón de navegación del sidebar con estado activo."""
    
    def __init__(self, parent, icon, label, command):
        """
        Inicializa el botón de navegación.
        
        Args:
            parent: Widget padre
            icon: Emoji del ícono
            label: Texto del botón
            command: Callback al hacer click
        """
        super().__init__(parent, bg=COLORS["sidebar_bg"], cursor="hand2")
        
        self.command = command
        self._active = False
        
        # Indicador vertical (barra azul cuando activo)
        self.indicator = tk.Frame(
            self,
            width=4,
            bg=COLORS["sidebar_bg"]
        )
        self.indicator.pack(side="left", fill="y")
        
        # Contenedor interno
        self.inner = tk.Frame(
            self,
            bg=COLORS["sidebar_bg"],
            pady=10,
            padx=12
        )
        self.inner.pack(side="left", fill="both", expand=True)
        
        # Label con ícono + texto
        self.label = tk.Label(
            self.inner,
            text=f"{icon}  {label}",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            font=FONTS["body"],
            anchor="w",
        )
        self.label.pack(fill="x")
        
        # Bind clicks en todos los widgets
        for widget in (self, self.inner, self.label):
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def set_active(self, active: bool):
        """Cambia el estado activo del botón."""
        self._active = active
        
        # Colores según estado
        bg_color = COLORS["sidebar_active"] if active else COLORS["sidebar_bg"]
        fg_color = COLORS["sidebar_text_active"] if active else COLORS["sidebar_text"]
        indicator_color = COLORS["primary"] if active else COLORS["sidebar_bg"]
        
        # Aplicar colores
        self.indicator.configure(bg=indicator_color)
        self.configure(bg=bg_color)
        self.inner.configure(bg=bg_color)
        self.label.configure(bg=bg_color, fg=fg_color)
    
    def _on_enter(self, event=None):
        """Efecto hover al pasar el mouse."""
        if not self._active:
            hover_bg = COLORS["sidebar_hover"]
            self.configure(bg=hover_bg)
            self.inner.configure(bg=hover_bg)
            self.label.configure(bg=hover_bg)
    
    def _on_leave(self, event=None):
        """Efecto al salir el mouse."""
        if not self._active:
            normal_bg = COLORS["sidebar_bg"]
            self.configure(bg=normal_bg)
            self.inner.configure(bg=normal_bg)
            self.label.configure(bg=normal_bg)
```

### 2. Tooltip

**Archivo:** `src/ui/components/tooltip.py`

```python
"""
Tooltip que aparece al hacer hover sobre un widget
"""

import tkinter as tk
from ui.styles import COLORS, FONTS


class Tooltip:
    """
    Tooltip simple que aparece al hacer hover.
    
    Uso:
        Tooltip(widget, title="Título", body="Descripción")
    """
    
    def __init__(self, widget, title: str, body: str = ""):
        """
        Inicializa el tooltip.
        
        Args:
            widget: Widget sobre el que aparecerá el tooltip
            title: Título del tooltip
            body: Descripción (opcional)
        """
        self.widget = widget
        self.title = title
        self.body = body
        self.tw = None  # Ventana del tooltip
        
        # Bind eventos
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    
    def show(self, event=None):
        """Muestra el tooltip."""
        # Calcular posición (debajo del widget)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        
        # Crear ventana toplevel
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # Sin decoración de ventana
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.configure(bg=COLORS["text_primary"])
        
        # Contenido
        frame = tk.Frame(
            self.tw,
            bg=COLORS["text_primary"],
            padx=12,
            pady=8
        )
        frame.pack()
        
        # Título
        if self.title:
            tk.Label(
                frame,
                text=self.title,
                bg=COLORS["text_primary"],
                fg="white",
                font=FONTS["badge"],
            ).pack(anchor="w")
        
        # Cuerpo
        if self.body:
            tk.Label(
                frame,
                text=self.body,
                bg=COLORS["text_primary"],
                fg="#A8B8CC",
                font=FONTS["small"],
                wraplength=240,
                justify="left",
            ).pack(anchor="w", pady=(2, 0))
    
    def hide(self, event=None):
        """Oculta el tooltip."""
        if self.tw:
            self.tw.destroy()
            self.tw = None
```

### 3. Modismo Tag (con Tooltip Interactivo)

**Archivo:** `src/ui/components/modism_tag.py`

```python
"""
Tooltip interactivo para modismos con botones de acción
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import COLORS, FONTS


class ModismTooltip(tk.Toplevel):
    """
    Tooltip interactivo que aparece sobre modismos detectados.
    Incluye botones: Aceptar, Editar, Ignorar
    """
    
    def __init__(self, parent, modismo_original: str, sugerencia: str, 
                 position: tuple, on_action=None):
        """
        Inicializa el tooltip de modismo.
        
        Args:
            parent: Widget padre
            modismo_original: Expresión original detectada
            sugerencia: Expresión normalizada sugerida
            position: Tupla (x, y) de posición en pantalla
            on_action: Callback(action: str) cuando se hace click en botón
        """
        super().__init__(parent)
        
        self.modismo_original = modismo_original
        self.sugerencia = sugerencia
        self.on_action = on_action
        
        # Configurar ventana
        self.wm_overrideredirect(True)
        self.wm_geometry(f"+{position[0]}+{position[1]}")
        self.configure(bg=COLORS["text_primary"])
        
        self._build_content()
    
    def _build_content(self):
        """Construye el contenido del tooltip."""
        frame = tk.Frame(
            self,
            bg=COLORS["text_primary"],
            padx=12,
            pady=10
        )
        frame.pack()
        
        # Texto original
        tk.Label(
            frame,
            text=f'Original: "{self.modismo_original}"',
            bg=COLORS["text_primary"],
            fg="white",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        
        # Sugerencia
        tk.Label(
            frame,
            text=f'→ "{self.sugerencia}"',
            bg=COLORS["text_primary"],
            fg="#A8B8CC",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(2, 10))
        
        # Botones de acción
        btn_frame = tk.Frame(frame, bg=COLORS["text_primary"])
        btn_frame.pack()
        
        # Botón Aceptar
        ttk.Button(
            btn_frame,
            text="✓ Aceptar",
            style="Success.TButton",
            command=lambda: self._handle_action("accept"),
            width=10
        ).pack(side="left", padx=2)
        
        # Botón Editar
        ttk.Button(
            btn_frame,
            text="✎ Editar",
            style="Secondary.TButton",
            command=lambda: self._handle_action("edit"),
            width=10
        ).pack(side="left", padx=2)
        
        # Botón Ignorar
        ttk.Button(
            btn_frame,
            text="✕ Ignorar",
            style="Secondary.TButton",
            command=lambda: self._handle_action("ignore"),
            width=10
        ).pack(side="left", padx=2)
    
    def _handle_action(self, action: str):
        """
        Maneja el click en un botón de acción.
        
        Args:
            action: "accept", "edit", o "ignore"
        """
        if self.on_action:
            self.on_action(action, self.modismo_original, self.sugerencia)
        
        self.destroy()
```

### 4. Timeline de Audio

**Archivo:** `src/ui/components/audio_timeline.py`

```python
"""
Timeline de audio con controles de reproducción
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import COLORS, FONTS


class AudioTimeline(tk.Frame):
    """
    Timeline de audio interactivo.
    Muestra tiempo actual, barra de progreso y controles.
    """
    
    def __init__(self, parent, duration: int = 0):
        """
        Inicializa el timeline.
        
        Args:
            parent: Widget padre
            duration: Duración total del audio en segundos
        """
        super().__init__(parent, bg=COLORS["card_bg"], height=60)
        
        self.duration = duration
        self.current_time = 0
        self.is_playing = False
        
        self._build()
    
    def _build(self):
        """Construye el timeline."""
        # Botón play/pause
        self.play_btn = ttk.Button(
            self,
            text="▶",
            style="Secondary.TButton",
            command=self.toggle_play,
            width=3
        )
        self.play_btn.pack(side="left", padx=10)
        
        # Tiempo actual
        self.time_label = tk.Label(
            self,
            text=self._format_time(0),
            font=FONTS["body"],
            bg=COLORS["card_bg"],
            fg=COLORS["text_primary"]
        )
        self.time_label.pack(side="left", padx=5)
        
        # Barra de progreso (timeline)
        self.progress = ttk.Progressbar(
            self,
            style="Blue.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=10)
        
        # Tiempo total
        self.duration_label = tk.Label(
            self,
            text=self._format_time(self.duration),
            font=FONTS["body"],
            bg=COLORS["card_bg"],
            fg=COLORS["text_primary"]
        )
        self.duration_label.pack(side="left", padx=5)
        
        # Control de volumen
        tk.Label(
            self,
            text="🔊",
            bg=COLORS["card_bg"],
            font=("Segoe UI", 12)
        ).pack(side="left", padx=10)
    
    def toggle_play(self):
        """Alterna entre play y pause."""
        self.is_playing = not self.is_playing
        self.play_btn.configure(text="⏸" if self.is_playing else "▶")
    
    def update_time(self, seconds: int):
        """
        Actualiza el tiempo actual.
        
        Args:
            seconds: Tiempo actual en segundos
        """
        self.current_time = seconds
        self.time_label.configure(text=self._format_time(seconds))
        
        # Actualizar barra de progreso
        if self.duration > 0:
            progress_percent = (seconds / self.duration) * 100
            self.progress["value"] = progress_percent
    
    def _format_time(self, seconds: int) -> str:
        """
        Formatea segundos a MM:SS.
        
        Args:
            seconds: Tiempo en segundos
            
        Returns:
            String formateado "MM:SS"
        """
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
```

---

## 📱 PANTALLA 1: DASHBOARD

**Archivo:** `src/ui/views/dashboard.py`

```python
"""
Vista Dashboard - Pantalla principal
Muestra estadísticas y actas recientes
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import COLORS, FONTS, DIMENSIONS


class DashboardView(tk.Frame):
    """Vista del Dashboard principal."""
    
    VIEW_NAME = "dashboard"
    
    def __init__(self, parent):
        """
        Inicializa la vista Dashboard.
        
        Args:
            parent: Widget padre (container)
        """
        super().__init__(parent, bg=COLORS["bg"])
        self._build()
    
    def _build(self):
        """Construye todos los elementos de la vista."""
        self._build_header()
        self._build_stats_cards()
        self._build_recent_sessions()
    
    def _build_header(self):
        """Construye el header con título y botón."""
        header = tk.Frame(
            self,
            bg=COLORS["bg"],
            pady=24,
            padx=DIMENSIONS["padding_large"]
        )
        header.pack(fill="x")
        
        # Título
        tk.Label(
            header,
            text="Dashboard",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=FONTS["title"],
        ).pack(side="left")
        
        # Botón Nueva Acta
        ttk.Button(
            header,
            text="+ Nueva Acta",
            style="Primary.TButton",
            command=self._on_new_session,
        ).pack(side="right")
    
    def _build_stats_cards(self):
        """Construye las tarjetas de estadísticas (KPIs)."""
        kpi_frame = tk.Frame(
            self,
            bg=COLORS["bg"],
            padx=DIMENSIONS["padding_large"]
        )
        kpi_frame.pack(fill="x")
        
        # Configurar grid
        for col in range(4):
            kpi_frame.columnconfigure(col, weight=1, uniform="kpi")
        
        # Datos de KPIs
        kpis = [
            ("12", "Actas procesadas", COLORS["primary"]),
            ("95%", "Precisión promedio", COLORS["success"]),
            ("8.5h", "Horas transcritas", COLORS["primary"]),
            ("47", "Modismos detectados", COLORS["warning"]),
        ]
        
        # Crear cards
        for col, (value, label, color) in enumerate(kpis):
            card = self._create_kpi_card(kpi_frame, value, label, color)
            card.grid(
                row=0,
                column=col,
                sticky="ew",
                padx=(0, 16) if col < 3 else 0
            )
    
    def _create_kpi_card(self, parent, value: str, label: str, color: str):
        """
        Crea una tarjeta KPI.
        
        Args:
            parent: Widget padre
            value: Valor numérico a mostrar
            label: Label descriptivo
            color: Color del borde y valor
            
        Returns:
            Frame de la tarjeta
        """
        card = tk.Frame(
            parent,
            bg=COLORS["card_bg"],
            padx=24,
            pady=20,
        )
        
        # Borde izquierdo coloreado (simulado con Frame)
        accent = tk.Frame(card, bg=color, width=4)
        accent.place(relheight=1, x=0, y=0)
        
        # Contenedor interno
        inner = tk.Frame(card, bg=COLORS["card_bg"], padx=12)
        inner.pack(fill="both", expand=True)
        
        # Valor
        tk.Label(
            inner,
            text=value,
            bg=COLORS["card_bg"],
            fg=color,
            font=("Segoe UI", 28, "bold"),
        ).pack(anchor="w")
        
        # Label
        tk.Label(
            inner,
            text=label,
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"],
        ).pack(anchor="w")
        
        return card
    
    def _build_recent_sessions(self):
        """Construye la tabla de sesiones recientes."""
        frame = tk.Frame(
            self,
            bg=COLORS["bg"],
            padx=DIMENSIONS["padding_large"],
            pady=24
        )
        frame.pack(fill="both", expand=True)
        
        # Título de sección
        tk.Label(
            frame,
            text="Últimas Actas Procesadas",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 12))
        
        # Tabla con Treeview
        columns = ("Nombre", "Fecha", "Duración", "Estado")
        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=5
        )
        
        # Configurar columnas
        tree.heading("Nombre", text="Nombre")
        tree.heading("Fecha", text="Fecha")
        tree.heading("Duración", text="Duración")
        tree.heading("Estado", text="Estado")
        
        tree.column("Nombre", width=300, anchor="w")
        tree.column("Fecha", width=120, anchor="center")
        tree.column("Duración", width=100, anchor="center")
        tree.column("Estado", width=150, anchor="center")
        
        # Datos de ejemplo
        rows = [
            ("Reunion_Proyecto_X.docx", "24 Feb 2026", "45 min", "✅ Procesada"),
            ("Planificacion_Q1.docx", "23 Feb 2026", "1h 15min", "✅ Procesada"),
            ("Standup_Semanal.docx", "22 Feb 2026", "22 min", "🟠 En edición"),
            ("Revision_Presupuesto.docx", "20 Feb 2026", "2h 05min", "✅ Procesada"),
            ("Entrevista_Lead_Dev.docx", "18 Feb 2026", "38 min", "✅ Procesada"),
        ]
        
        for row in rows:
            tree.insert("", "end", values=row)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        
        # Botón "Ver todas"
        ttk.Button(
            frame,
            text="Ver todas →",
            style="Secondary.TButton",
        ).pack(anchor="e", pady=(8, 0))
    
    def _on_new_session(self):
        """Handler para botón 'Nueva Acta'."""
        # Navegar a vista de transcripción
        # (esto será manejado por el app principal)
        print("Navegando a Transcripción...")
```

---

## 🎙️ PANTALLA 2: TRANSCRIPCIÓN EN VIVO

**Archivo:** `src/ui/views/transcription.py`

```python
"""
Vista Transcripción en Vivo
Procesamiento de audio y detección de modismos en tiempo real
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from ui.styles import COLORS, FONTS, DIMENSIONS
from ui.components.tooltip import Tooltip
from ui.components.modism_tag import ModismTooltip
from ui.components.audio_timeline import AudioTimeline


class TranscriptionView(tk.Frame):
    """Vista de transcripción en vivo."""
    
    VIEW_NAME = "transcription"
    
    def __init__(self, parent):
        """
        Inicializa la vista de transcripción.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent, bg=COLORS["bg"])
        
        # Estado
        self._recording = False
        self._audio_path = None
        
        self._build()
    
    def _build(self):
        """Construye todos los elementos de la vista."""
        self._build_header()
        self._build_controls()
        self._build_body()
    
    def _build_header(self):
        """Construye el header con título e indicador LIVE."""
        header = tk.Frame(
            self,
            bg=COLORS["bg"],
            pady=20,
            padx=DIMENSIONS["padding_large"]
        )
        header.pack(fill="x")
        
        # Título
        tk.Label(
            header,
            text="Transcripción en vivo",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=FONTS["title"],
        ).pack(side="left")
        
        # Indicador LIVE (oculto inicialmente)
        self.live_indicator = tk.Label(
            header,
            text="● EN VIVO",
            bg=COLORS["bg"],
            fg=COLORS["live_red"],
            font=FONTS["badge"],
        )
        # No hacer pack() hasta que se inicie grabación
    
    def _build_controls(self):
        """Construye los controles de audio."""
        ctrl = tk.Frame(
            self,
            bg=COLORS["card_bg"],
            padx=DIMENSIONS["padding_large"],
            pady=16
        )
        ctrl.pack(fill="x", padx=DIMENSIONS["padding_large"], pady=(0, 8))
        
        # Botón Importar
        ttk.Button(
            ctrl,
            text="📁 Importar",
            style="Secondary.TButton",
            command=self._on_import_audio,
        ).pack(side="left", padx=(0, 12))
        
        # Botón Grabar
        self.rec_btn = ttk.Button(
            ctrl,
            text="⏺  Grabar",
            style="Primary.TButton",
            command=self._toggle_recording,
        )
        self.rec_btn.pack(side="left", padx=(0, 24))
        
        # Separador vertical
        ttk.Separator(ctrl, orient="vertical").pack(
            side="left",
            fill="y",
            padx=12
        )
        
        # Selector de idioma
        tk.Label(
            ctrl,
            text="Idioma:",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
        ).pack(side="left", padx=(0, 8))
        
        self.lang_var = tk.StringVar(value="Español")
        ttk.Combobox(
            ctrl,
            textvariable=self.lang_var,
            values=["Español", "Inglés"],
            width=12,
            state="readonly",
        ).pack(side="left")
    
    def _build_body(self):
        """Construye el área principal (texto + timeline + botones)."""
        # Timeline de audio
        self.timeline = AudioTimeline(self, duration=0)
        self.timeline.pack(
            fill="x",
            padx=DIMENSIONS["padding_large"],
            pady=(0, 8)
        )
        
        # Área de transcripción
        self._build_transcript_area()
        
        # Barra de progreso
        self._build_progress_bar()
        
        # Botones de acción
        self._build_action_buttons()
    
    def _build_transcript_area(self):
        """Construye el área de texto con transcripción."""
        card = tk.Frame(
            self,
            bg=COLORS["card_bg"],
            padx=24,
            pady=20,
        )
        card.pack(
            fill="both",
            expand=True,
            padx=DIMENSIONS["padding_large"],
            pady=(0, 8)
        )
        
        # Título
        tk.Label(
            card,
            text="Transcripción",
            bg=COLORS["card_bg"],
            fg=COLORS["text_primary"],
            font=FONTS["heading"],
        ).pack(anchor="w", pady=(0, 8))
        
        # Frame para texto con borde
        txt_frame = tk.Frame(card, bg=COLORS["border"], pady=1, padx=1)
        txt_frame.pack(fill="both", expand=True)
        
        # Widget Text
        self.txt = tk.Text(
            txt_frame,
            font=FONTS["body"],
            bg="white",
            fg=COLORS["text_primary"],
            relief="flat",
            wrap="word",
            padx=16,
            pady=12,
            spacing2=4,  # Espaciado entre líneas
        )
        
        # Tag para modismos detectados
        self.txt.tag_configure(
            "modismo",
            background=COLORS["warning_light"],
            foreground=COLORS["warning"],
            underline=True,
        )
        
        # Tag para timestamps
        self.txt.tag_configure(
            "timestamp",
            foreground=COLORS["text_secondary"],
            font=FONTS["small"],
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(txt_frame, command=self.txt.yview)
        self.txt.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.txt.pack(fill="both", expand=True)
        
        # Texto de ejemplo
        self._insert_sample_text()
        
        # Bind click en modismos
        self.txt.tag_bind("modismo", "<Button-1>", self._on_modismo_click)
    
    def _insert_sample_text(self):
        """Inserta texto de ejemplo con modismos."""
        sample_text = """[10:02] Gerente: Buenos días a todos. Necesitamos revisar el avance del proyecto antes de que alguien meta el pie en el proceso.

[10:05] Analista: Entendido. El equipo ha dado en el clavo con la solución propuesta la semana pasada. Me tinca que deberíamos priorizar el módulo de reportes.

[10:08] Gerente: Estoy de acuerdo. Además, necesitamos revisar los pendientes de la integración con el API de pagos."""
        
        self.txt.insert("1.0", sample_text)
        
        # Resaltar timestamps
        self._highlight_timestamps()
        
        # Resaltar modismos
        self._highlight_modismo("meta el pie")
        self._highlight_modismo("dado en el clavo")
        self._highlight_modismo("me tinca")
        
        self.txt.configure(state="disabled")
    
    def _highlight_timestamps(self):
        """Resalta todos los timestamps [HH:MM]."""
        import re
        content = self.txt.get("1.0", "end")
        
        for match in re.finditer(r'\[\d{2}:\d{2}\]', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.txt.tag_add("timestamp", start_idx, end_idx)
    
    def _highlight_modismo(self, phrase: str):
        """
        Resalta todas las ocurrencias de un modismo.
        
        Args:
            phrase: Frase a resaltar
        """
        start = "1.0"
        while True:
            pos = self.txt.search(phrase, start, stopindex="end", nocase=True)
            if not pos:
                break
            
            end = f"{pos}+{len(phrase)}c"
            self.txt.tag_add("modismo", pos, end)
            start = end
    
    def _build_progress_bar(self):
        """Construye la barra de progreso de transcripción."""
        progress_frame = tk.Frame(
            self,
            bg=COLORS["bg"],
            padx=DIMENSIONS["padding_large"]
        )
        progress_frame.pack(fill="x", pady=(0, 8))
        
        # Label de estado
        self.progress_label = tk.Label(
            progress_frame,
            text="Transcribiendo... 45% | Tiempo estimado: 2 min",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"],
        )
        self.progress_label.pack(anchor="w", pady=(0, 4))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="Blue.Horizontal.TProgressbar",
            mode="determinate",
            value=45
        )
        self.progress_bar.pack(fill="x")
        
        # Ocultar inicialmente
        progress_frame.pack_forget()
        self.progress_frame = progress_frame
    
    def _build_action_buttons(self):
        """Construye los botones de acción inferiores."""
        btn_frame = tk.Frame(
            self,
            bg=COLORS["bg"],
            padx=DIMENSIONS["padding_large"],
            pady=16
        )
        btn_frame.pack(fill="x")
        
        # Botón Pausar
        ttk.Button(
            btn_frame,
            text="⏸  Pausar",
            style="Secondary.TButton",
        ).pack(side="left", padx=(0, 12))
        
        # Botón Cancelar
        ttk.Button(
            btn_frame,
            text="✕ Cancelar",
            style="Secondary.TButton",
        ).pack(side="left")
        
        # Botón Continuar (derecha)
        ttk.Button(
            btn_frame,
            text="Continuar a Normalización →",
            style="Primary.TButton",
        ).pack(side="right")
    
    def _on_import_audio(self):
        """Handler para importar audio."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar audio",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.m4a"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*"),
            ]
        )
        
        if filepath:
            self._audio_path = filepath
            print(f"Audio seleccionado: {filepath}")
            # Aquí llamarías al backend para procesar
    
    def _toggle_recording(self):
        """Alterna entre iniciar y detener grabación."""
        self._recording = not self._recording
        
        if self._recording:
            # Iniciar grabación
            self.rec_btn.configure(
                text="⏹  Detener grabación",
                style="Danger.TButton"
            )
            self.live_indicator.pack(side="left", padx=16)
            self.progress_frame.pack(fill="x", pady=(0, 8))
            
        else:
            # Detener grabación
            self.rec_btn.configure(
                text="⏺  Grabar",
                style="Primary.TButton"
            )
            self.live_indicator.pack_forget()
            self.progress_frame.pack_forget()
    
    def _on_modismo_click(self, event):
        """
        Handler cuando se hace click en un modismo.
        
        Args:
            event: Evento de click
        """
        # Obtener posición del click
        index = self.txt.index(f"@{event.x},{event.y}")
        
        # Obtener rangos de todos los tags "modismo" en esa posición
        tags = self.txt.tag_names(index)
        
        if "modismo" in tags:
            # Encontrar el rango del modismo
            ranges = self.txt.tag_ranges("modismo")
            
            for i in range(0, len(ranges), 2):
                start, end = ranges[i], ranges[i+1]
                
                # Verificar si el click está dentro de este rango
                if self.txt.compare(index, ">=", start) and \
                   self.txt.compare(index, "<=", end):
                    
                    # Obtener texto del modismo
                    modismo_text = self.txt.get(start, end)
                    
                    # Calcular posición para tooltip
                    bbox = self.txt.bbox(start)
                    if bbox:
                        x = self.txt.winfo_rootx() + bbox[0]
                        y = self.txt.winfo_rooty() + bbox[1] + bbox[3]
                        
                        # Mostrar tooltip interactivo
                        ModismTooltip(
                            self,
                            modismo_original=modismo_text,
                            sugerencia="expresión formal equivalente",
                            position=(x, y),
                            on_action=self._on_modismo_action
                        )
                    break
    
    def _on_modismo_action(self, action: str, original: str, sugerencia: str):
        """
        Handler cuando se hace click en un botón del tooltip.
        
        Args:
            action: "accept", "edit", o "ignore"
            original: Texto original del modismo
            sugerencia: Sugerencia de normalización
        """
        print(f"Acción: {action}, Original: {original}, Sugerencia: {sugerencia}")
        
        if action == "accept":
            # Reemplazar modismo con sugerencia
            pass
        elif action == "edit":
            # Abrir dialog para editar
            pass
        # "ignore" no hace nada
```

---

## 📤 PANTALLA 3: EXPORTACIÓN

**Archivo:** `src/ui/views/export.py`

```python
"""
Vista Exportación
Configuración y generación de documentos finales
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.styles import COLORS, FONTS, DIMENSIONS


class ExportView(tk.Frame):
    """Vista de exportación y estructuración de actas."""
    
    VIEW_NAME = "export"
    
    def __init__(self, parent):
        """
        Inicializa la vista de exportación.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent, bg=COLORS["bg"])
        
        # Variables de formulario
        self._titulo_var = tk.StringVar(value="Reunión de Planificación Proyecto Alpha")
        self._fecha_var = tk.StringVar(value="24-02-2026 10:00")
        self._participantes_var = tk.StringVar()
        self._objetivo_var = tk.StringVar(value="Definir hitos y cronograma Q1")
        
        # Variables de checkboxes
        self._include_acuerdos = tk.BooleanVar(value=True)
        self._include_tareas = tk.BooleanVar(value=True)
        self._include_compromisos = tk.BooleanVar(value=True)
        self._include_notas = tk.BooleanVar(value=False)
        
        # Variables de formato
        self._formato_doc = tk.StringVar(value="DOCX")
        self._formato_audio = tk.StringVar(value="MP3")
        self._guardar_local = tk.BooleanVar(value=True)
        
        self._build()
    
    def _build(self):
        """Construye todos los elementos de la vista."""
        self._build_header()
        self._build_body()
    
    def _build_header(self):
        """Construye el header con botón de retroceso."""
        header = tk.Frame(
            self,
            bg=COLORS["bg"],
            pady=20,
            padx=DIMENSIONS["padding_large"]
        )
        header.pack(fill="x")
        
        # Botón retroceder
        tk.Label(
            header,
            text="← Estructura del Acta",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=FONTS["title"],
            cursor="hand2"
        ).pack(side="left")
        
        # Badge "Listo para exportar"
        badge = tk.Frame(
            header,
            bg=COLORS["success"],
            padx=12,
            pady=6
        )
        badge.pack(side="right")
        
        tk.Label(
            badge,
            text="✓ Listo para exportar",
            bg=COLORS["success"],
            fg="white",
            font=FONTS["badge"]
        ).pack()
    
    def _build_body(self):
        """Construye el cuerpo en 2 columnas."""
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(
            fill="both",
            expand=True,
            padx=DIMENSIONS["padding_large"],
            pady=8
        )
        
        # Configurar grid
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)
        
        # Columna izquierda: Formulario
        self._build_form_column(body)
        
        # Columna derecha: Preview
        self._build_preview_column(body)
        
        # Panel inferior: Opciones de exportación
        self._build_export_options()
    
    def _build_form_column(self, parent):
        """Construye la columna izquierda con formulario."""
        card = tk.Frame(
            parent,
            bg=COLORS["card_bg"],
            padx=24,
            pady=24
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Título de la reunión
        tk.Label(
            card,
            text="Título de la reunión",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", pady=(0, 4))
        
        ttk.Entry(
            card,
            textvariable=self._titulo_var,
            font=FONTS["body"]
        ).pack(fill="x", pady=(0, 16))
        
        # Fecha y hora
        tk.Label(
            card,
            text="Fecha y hora",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", pady=(0, 4))
        
        ttk.Entry(
            card,
            textvariable=self._fecha_var,
            font=FONTS["body"]
        ).pack(fill="x", pady=(0, 16))
        
        # Participantes
        tk.Label(
            card,
            text="Participantes",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", pady=(0, 4))
        
        participantes_txt = tk.Text(
            card,
            height=4,
            font=FONTS["body"],
            wrap="word"
        )
        participantes_txt.pack(fill="x", pady=(0, 16))
        participantes_txt.insert("1.0", "Juan Pérez (PM)\nMaría González (Diseño)\nCarlos Ruiz (Dev)\nAna López (QA)")
        
        # Objetivo
        tk.Label(
            card,
            text="Objetivo",
            bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"]
        ).pack(anchor="w", pady=(0, 4))
        
        ttk.Entry(
            card,
            textvariable=self._objetivo_var,
            font=FONTS["body"]
        ).pack(fill="x", pady=(0, 24))
        
        # Secciones a incluir
        tk.Label(
            card,
            text="Secciones del acta",
            bg=COLORS["card_bg"],
            fg=COLORS["text_primary"],
            font=FONTS["heading"]
        ).pack(anchor="w", pady=(0, 12))
        
        checkboxes = [
            (self._include_acuerdos, "Acuerdos alcanzados"),
            (self._include_tareas, "Tareas asignadas y responsables"),
            (self._include_compromisos, "Compromisos pendientes"),
            (self._include_notas, "Notas adicionales"),
        ]
        
        for var, label in checkboxes:
            ttk.Checkbutton(
                card,
                text=label,
                variable=var,
                style="TCheckbutton"
            ).pack(anchor="w", pady=4)
    
    def _build_preview_column(self, parent):
        """Construye la columna derecha con preview."""
        card = tk