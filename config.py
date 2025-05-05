import os
from tkinter import ttk
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()

class ThemeConfig(TypedDict):
    bg: str
    fg: str
    font: tuple[str, int]
    button_bg: str
    button_fg: str
    error: str
    success: str

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'farmacia')
    APP_TITLE = "farmacia"
    
    THEME: ThemeConfig = {
        'bg': '#1E1E1E',          # Fondo oscuro
        'fg': '#E0E0E0',          # Texto claro
        'font': ('Segoe UI', 11),
        'button_bg': '#7C4DFF',   # Morado vibrante
        'button_fg': '#555555',   # Texto blanco
        'error': '#FF5252',       # Rojo claro
        'success': '#69F0AE',     # Verde menta
        'warning': '#FFD740',     # Amarillo ámbar
        'accent': '#448AFF',      # Azul brillante (para resaltar elementos)
        'border': '#424242',      # Bordes sutiles
    }
    
    @staticmethod
    def setup_styles(style: ttk.Style) -> None:
        style.configure('TFrame', background=Config.THEME['bg'])
        style.configure('TLabel', 
                      background=Config.THEME['bg'],
                      foreground=Config.THEME['fg'],
                      font=Config.THEME['font'])
        style.configure('TButton',
                      background=Config.THEME['button_bg'],
                      foreground=Config.THEME['button_fg'],
                      font=Config.THEME['font'])
        style.configure('Error.TLabel', foreground=Config.THEME['error'])
        style.configure('Success.TLabel', foreground=Config.THEME['success'])