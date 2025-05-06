# config.py (farmacia)
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
    DB_NAME = os.getenv('DB_NAME', 'farmacia_db')
    APP_TITLE = "Sistema de Farmacia"
    
    THEME: ThemeConfig = {
        'bg': '#1E1E1E',
        'fg': '#E0E0E0',
        'font': ('Segoe UI', 11),
        'button_bg': '#4CAF50',  # Verde farmacia
        'button_fg': '#FFFFFF',
        'error': '#FF5252',
        'success': '#69F0AE',
        'warning': '#FFD740',
        'accent': '#8BC34A',     # Verde claro
        'border': '#424242',
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