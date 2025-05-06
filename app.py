import tkinter as tk
from tkinter import ttk
from login import LoginForm
from config import Config

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(Config.APP_TITLE)
        self.root.geometry("400x300")
        self.root.configure(bg=Config.THEME['bg'])
        
        # Configurar el estilo
        style = ttk.Style()
        Config.setup_styles(style)
        
        # Mostrar el formulario de login
        LoginForm(self.root)
        
        self.root.mainloop()

if __name__ == "__main__":
    App()