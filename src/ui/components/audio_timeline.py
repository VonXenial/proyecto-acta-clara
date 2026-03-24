"""
Timeline de audio con controles de reproducción
"""

import tkinter as tk
from tkinter import ttk
from src.ui.styles import COLORS, FONTS

class AudioTimeline(tk.Frame):
    """
    Timeline de audio interactivo.
    """
    
    def __init__(self, parent, duration: int = 0, theme: str = "light"):
        self.c = COLORS[theme]
        super().__init__(parent, bg=self.c["card_bg"], height=60)
        
        self.duration = duration
        self.current_time = 0
        self.is_playing = False
        
        self._build()
    
    def _build(self):
        c = self.c

        self.play_btn = ttk.Button(self, text="▶", style="Secondary.TButton", 
                                   command=self.toggle_play, width=3)
        self.play_btn.pack(side="left", padx=10)
        
        self.time_label = tk.Label(self, text=self._format_time(0), font=FONTS["body"], 
                                   bg=c["card_bg"], fg=c["text_primary"])
        self.time_label.pack(side="left", padx=5)
        
        self.progress = ttk.Progressbar(self, style="Blue.Horizontal.TProgressbar", 
                                         mode="determinate", maximum=100)
        self.progress.pack(side="left", fill="x", expand=True, padx=10)
        
        self.duration_label = tk.Label(self, text=self._format_time(self.duration), 
                                       font=FONTS["body"], bg=c["card_bg"], fg=c["text_primary"])
        self.duration_label.pack(side="left", padx=5)
        
        tk.Label(self, text="🔊", bg=c["card_bg"], font=("Segoe UI", 12)).pack(side="left", padx=10)
    
    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_btn.configure(text="⏸" if self.is_playing else "▶")
    
    def update_time(self, seconds: int):
        self.current_time = seconds
        self.time_label.configure(text=self._format_time(seconds))
        if self.duration > 0:
            progress_percent = (seconds / self.duration) * 100
            self.progress["value"] = progress_percent
    
    def _format_time(self, seconds: int) -> str:
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"
