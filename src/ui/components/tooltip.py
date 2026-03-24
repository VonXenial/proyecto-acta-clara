"""
Tooltip que aparece al hacer hover sobre un widget
"""

import tkinter as tk
from src.ui.styles import COLORS, FONTS

class Tooltip:
    """
    Tooltip simple que aparece al hacer hover.
    """
    
    def __init__(self, widget, title: str, body: str = "", theme: str = "light"):
        self.widget = widget
        self.title = title
        self.body = body
        self.c = COLORS[theme]
        self.tw = None
        
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    
    def show(self, event=None):
        c = self.c
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.configure(bg=c["text_primary"])
        
        frame = tk.Frame(self.tw, bg=c["text_primary"], padx=12, pady=8)
        frame.pack()
        
        if self.title:
            tk.Label(frame, text=self.title, bg=c["text_primary"], 
                     fg="white", font=FONTS["badge"]).pack(anchor="w")
        
        if self.body:
            tk.Label(frame, text=self.body, bg=c["text_primary"], 
                     fg="#A8B8CC", font=FONTS["small"], wraplength=240, justify="left").pack(anchor="w", pady=(2, 0))
    
    def hide(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None
