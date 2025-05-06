import tkinter as tk
from tkinter import ttk, messagebox
from views.base_form import BaseForm
from db.user_dao import UserDAO
from config import Config

class LoginForm(BaseForm):
    def __init__(self, parent):
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        super().__init__(parent, "Inicio de Sesión", 350, 300)
        
        self.dao = UserDAO()
        self._create_widgets()
        self._center_window()
        self.bind("<Return>", lambda event: self._login())  # Bind Enter key to login

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            main_frame, 
            text=Config.APP_TITLE,
            font=('Arial', 16, 'bold'),
            foreground=Config.THEME['button_bg']
        ).pack(pady=(0, 20))

        # Campo Usuario
        ttk.Label(main_frame, text="Usuario:").pack(anchor='w')
        self.username_entry = ttk.Entry(
            main_frame, 
            textvariable=self.username_var,
            font=('Arial', 12)
        )
        self.username_entry.pack(fill='x', pady=5)

        # Campo Contraseña
        ttk.Label(main_frame, text="Contraseña:").pack(anchor='w')
        self.password_entry = ttk.Entry(
            main_frame,
            textvariable=self.password_var,
            show="*",
            font=('Arial', 12)
        )
        self.password_entry.pack(fill='x', pady=5)

        # Botón Login
        ttk.Button(
            main_frame,
            text="Iniciar Sesión",
            command=self._login,
            style='Accent.TButton'
        ).pack(fill='x', pady=(20, 0))

        self.username_entry.focus()

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username:
            messagebox.showerror("Error", "Usuario es requerido")
            return
            
        if not password:
            messagebox.showerror("Error", "Contraseña es requerida")
            return
            
        try:
            user = self.dao.get_by_username(username)
            if user and user.check_password(password):
                self.destroy()
                from menu import MenuApp
                #show menu app on top when login is successful
                
                MenuApp(self.master, user)
            
            else:
                messagebox.showerror("Error", "Credenciales inválidas")
                self.password_var.set('')
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar: {str(e)}")