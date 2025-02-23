import tkinter as tk
from abc import ABC, abstractmethod

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        # Determine the position for Tooltip
        if isinstance(self.widget, tk.Listbox):
            # For Listbox, use mouse pointer position
            x = self.widget.winfo_pointerx() + 10
            y = self.widget.winfo_pointery() + 10
        else:
            # For other widgets, use bbox of "insert" (e.g., Entry, Text)
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
        
        # Create Tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
class GUI(ABC):
    
    @abstractmethod
    def setup_ui(self):
        pass
    
    @abstractmethod
    def draw(self):
        pass
    
    
                
