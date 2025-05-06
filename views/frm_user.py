# views/frm_user.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.user import User
from db.user_dao import UserDAO
from views.base_form import BaseForm

class UserForm(BaseForm):
    def __init__(self, parent, current_user, user_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Usuario", 400, 350)
        self.current_user = current_user  # Usuario actual logueado
        self.dao = UserDAO()
        self.user = None
        self.user_id = user_id
        self._setup_permissions()
        
        self._create_widgets()
        self._load_data()

    def _setup_permissions(self):
        # Solo admin puede gestionar usuarios
        if self.current_user.perfil != 'admin':
            self.destroy()
            return
        
        # Si está editando su propio usuario, no permitir cambiar perfil
        if self.user_id and self.user_id == self.current_user.usuario_id:
            self.perfil_combo.config(state='disabled')
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Nombre:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = ttk.Entry(main_frame)
        self.nombre_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Contraseña:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Confirmar Contraseña:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.confirm_password_entry = ttk.Entry(main_frame, show="*")
        self.confirm_password_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Perfil:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.perfil_combo = ttk.Combobox(main_frame, values=["admin", "gerente", "cajero"], state='readonly')
        self.perfil_combo.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        # Barra de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky='e', pady=10)
        
        self.delete_btn = ttk.Button(
            button_frame, 
            text="Eliminar", 
            command=self._delete,
            style='Danger.TButton'
        )
        
        ttk.Button(
            button_frame, 
            text="Guardar", 
            command=self._save,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.destroy
        ).pack(side='left', padx=5)
        
        if self.user_id:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_data(self):
        if self.user_id:
            self.user = self.dao.get(self.user_id)
            if self.user:
                self.nombre_entry.insert(0, self.user.nombre)
                self.username_entry.insert(0, self.user.user_name)
                self.perfil_combo.set(self.user.perfil)
                # La contraseña no se carga por seguridad
    
    def _get_form_data(self) -> Optional[User]:
        nombre = self.nombre_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        perfil = self.perfil_combo.get()
        
        if not all([nombre, username, perfil]):
            self.show_error("Nombre, username y perfil son obligatorios")
            return None
            
        # Validar contraseña solo para nuevos usuarios o cuando se cambia
        if (not self.user_id or password) and password != confirm_password:
            self.show_error("Las contraseñas no coinciden")
            return None
            
        if (not self.user_id or password) and len(password) < 8:
            self.show_error("La contraseña debe tener al menos 8 caracteres")
            return None
            
        user = User(
            usuario_id=self.user_id,
            nombre=nombre,
            user_name=username,
            perfil=perfil
        )
        
        if password:
            user.set_password(password)
        elif self.user_id:
            # Mantener la contraseña existente si no se cambia
            user.password = self.user.password
            
        return user
    
    def _save(self):
        user = self._get_form_data()
        if not user:
            return
            
        if not user.validate():
            self.show_error("Datos del usuario no válidos")
            return
            
        if self.user_id:
            success = self.dao.update(user)
            msg = "actualizado"
        else:
            success = self.dao.save(user)
            msg = "creado"
            
        if success:
            self.show_success(f"Usuario {msg} correctamente")
            self.destroy()
        else:
            self.show_error(f"No se pudo {msg} el usuario")
    
    def _delete(self):
        if not self.user_id:
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este usuario?"):
            if self.dao.delete(self.user_id):
                self.show_success("Usuario eliminado correctamente")
                self.destroy()
            else:
                self.show_error("No se pudo eliminar el usuario")