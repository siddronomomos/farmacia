import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config import Config

class BaseForm(tk.Toplevel):
    def __init__(self, parent, title: str, width: int = 600, height: int = 400):
        super().__init__(parent)
        self.title(f"{Config.APP_TITLE} - {title}")
        self.geometry(f"{width}x{height}")
        self.configure(bg=Config.THEME['bg'])
        
        self.style = ttk.Style()
        Config.setup_styles(self.style)
        
        self._center_window()
        self.resizable(False, False)
    
    def _create_widgets(self):
        """Método que deben implementar las subclases para crear los widgets"""
        raise NotImplementedError("Las subclases deben implementar este método")
    
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        messagebox.showinfo("Éxito", message)
    
    def show_warning(self, message: str):
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning("Advertencia", message)
    
    def ask_confirmation(self, message: str) -> bool:
        """Pide confirmación al usuario"""
        return messagebox.askyesno("Confirmar", message)
    
    def create_frame(self, parent, padding: int = 10) -> ttk.Frame:
        """Crea un frame con padding"""
        frame = ttk.Frame(parent)
        frame.pack(padx=padding, pady=padding, fill='both', expand=True)
        return frame
    
    def create_label_entry(self, parent, text: str, row: int, var: Optional[tk.Variable] = None) -> ttk.Entry:
        """Crea un label y un entry en un grid"""
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        entry = ttk.Entry(parent, textvariable=var) if var else ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        return entry
    
    def create_button(self, parent, text: str, command, row: int, column: int) -> ttk.Button:
        """Crea un botón en una posición específica"""
        button = ttk.Button(parent, text=text, command=command)
        button.grid(row=row, column=column, padx=5, pady=5)
        return button
    
    def create_button_bar(self, parent, buttons: list[tuple[str, callable]]) -> ttk.Frame:
        """Crea una barra de botones"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=10)
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(frame, text=text, command=command).pack(side='left', padx=5)
            
        return frame