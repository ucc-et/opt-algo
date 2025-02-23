import tkinter as tk
from abc import ABC, abstractmethod

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, bg="lightyellow", relief="solid", borderwidth=1, padx=5, pady=2)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
class GUI(ABC):
    
    @abstractmethod
    def setup_ui(self):
        pass
    
    @abstractmethod
    def run_algorithm(self):
        pass
    
    @abstractmethod
    def draw(self):
        pass
    
    
                
