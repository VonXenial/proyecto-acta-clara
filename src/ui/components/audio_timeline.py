"""
Timeline de audio con controles de reproducción
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.ui.styles import COLORS, FONTS # type: ignore

class AudioTimeline(tk.Frame):
    """
    Timeline de audio interactivo con soporte para reproducción real y búsqueda (seeking).
    """
    
    def __init__(self, parent, audio_ctrl=None, theme: str = "light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["card_bg"], height=60)
        
        self.audio_ctrl = audio_ctrl
        self.duration = 0.0
        self.current_time = 0.0
        self.is_playing = False
        self._after_id: Optional[str] = None
        self._is_seeking = False
        
        # Inicialización de atributos UI para el linter
        self.play_btn: ttk.Button = None # type: ignore
        self.time_label: tk.Label = None # type: ignore
        self.progress: ttk.Scale = None # type: ignore
        self.seek_var: tk.DoubleVar = None # type: ignore
        self.duration_label: tk.Label = None # type: ignore
        self.vol_var: tk.DoubleVar = None # type: ignore
        self.vol_scale: ttk.Scale = None # type: ignore
        
        self._build()
    
    def _build(self):
        c = self.c

        # Play/Pause
        self.play_btn = ttk.Button(self, text="▶", style="Secondary.TButton", 
                                   command=self.toggle_play, width=3)
        self.play_btn.pack(side="left", padx=(10, 5))
        
        # Current Time
        self.time_label = tk.Label(self, text=self._format_time(0), font=FONTS["body"], 
                                   bg=c["card_bg"], fg=c["text_primary"])
        self.time_label.pack(side="left", padx=5)
        
        # Progress Scale (Timeline)
        self.seek_var = tk.DoubleVar(value=0)
        self.progress = ttk.Scale(self, from_=0, to=100, variable=self.seek_var, 
                                   orient="horizontal", command=self._on_seek)
        self.progress.pack(side="left", fill="x", expand=True, padx=10)
        self.progress.bind("<ButtonPress-1>", self._start_seek)
        self.progress.bind("<ButtonRelease-1>", self._end_seek)
        
        # Duration
        self.duration_label = tk.Label(self, text=self._format_time(0), 
                                       font=FONTS["body"], bg=c["card_bg"], fg=c["text_primary"])
        self.duration_label.pack(side="left", padx=5)
        
        # Volume Group
        vol_frame = tk.Frame(self, bg=c["card_bg"])
        vol_frame.pack(side="left", padx=(15, 10))
        
        tk.Label(vol_frame, text="🔊", bg=c["card_bg"], font=("Segoe UI", 11)).pack(side="left")
        
        self.vol_var = tk.DoubleVar(value=0.8)
        self.vol_scale = ttk.Scale(vol_frame, from_=0, to=1, variable=self.vol_var, 
                                   orient="horizontal", length=80, command=self._on_volume_change)
        self.vol_scale.pack(side="left", padx=5)
        
        if self.audio_ctrl:
            self.audio_ctrl.set_volume(0.8)

    def set_audio(self, file_path: str):
        """Asigna un nuevo audio al timeline."""
        if not self.audio_ctrl:
            return
        self.audio_ctrl.stop_playback()
        self.duration = self.audio_ctrl.load_playback_audio(file_path)
        
        if self.duration == 0:
            self.duration_label.configure(text="--:--", fg="red")
            print(f"[AudioTimeline] ADVERTENCIA: No se pudo cargar el audio. Verifica FFMPEG.")
        else:
            self.duration_label.configure(text=self._format_time(self.duration), fg=self.c["text_primary"])
            
        self.progress.configure(to=self.duration if self.duration > 0 else 100)
        self.update_time(0)
        self.is_playing = False
        self.play_btn.configure(text="▶")

    def toggle_play(self):
        if not self.audio_ctrl or self.duration == 0:
            return
        
        if self.is_playing:
            self.audio_ctrl.stop_playback()
            self.is_playing = False
            self.play_btn.configure(text="▶")
            if self._after_id:
                self.after_cancel(self._after_id) # type: ignore
                self._after_id = None
        else:
            # Si terminó, volver al inicio
            current = self.seek_var.get()
            if current >= self.duration - 0.1:
                current = 0
                
            self.audio_ctrl.play_audio(current)
            self.is_playing = True
            self.play_btn.configure(text="⏸")
            self._update_loop()

    def _update_loop(self):
        if not self.is_playing or not self.audio_ctrl or self._is_seeking:
            return
        
        pos = self.audio_ctrl.get_playback_pos()
        self.update_time(pos)
        
        if not self.audio_ctrl.is_playing():
            self.is_playing = False
            self.play_btn.configure(text="▶")
            # Forzar posición final si terminó
            if pos >= self.duration - 0.1:
                self.update_time(self.duration)
            return

        self._after_id = self.after(100, self._update_loop) # type: ignore

    def _start_seek(self, event):
        self._is_seeking = True

    def _end_seek(self, event):
        self._is_seeking = False
        if self.audio_ctrl and self.duration > 0:
            new_pos = self.seek_var.get()
            if self.is_playing:
                self.audio_ctrl.play_audio(new_pos)
            else:
                self.update_time(new_pos)

    def _on_seek(self, val):
        if self._is_seeking:
            self.time_label.configure(text=self._format_time(float(val)))

    def _on_volume_change(self, val):
        if self.audio_ctrl:
            self.audio_ctrl.set_volume(float(val))

    def update_time(self, seconds: float):
        self.current_time = seconds
        self.time_label.configure(text=self._format_time(seconds))
        if not self._is_seeking:
            self.seek_var.set(seconds)
    
    def _format_time(self, seconds: float) -> str:
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"
