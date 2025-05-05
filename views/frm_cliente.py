import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.cliente import Cliente
from db.cliente_dao import ClienteDAO
from views.base_form import BaseForm

class ClienteForm(BaseForm):
    def __init__(self, parent, user, cliente_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Cliente", 400, 300)
        self.user = user
        self.dao = ClienteDAO()
        self.cliente = None
        self.cliente_id = cliente_id
        
        self._create_widgets()
        self._load_data()
        self._setup_permissions()
    
    def _setup_permissions(self):
        if self.user.perfil == 'cajero' and self.cliente_id:
            self.nombre_entry.config(state='disabled')
            self.telefono_entry.config(state='disabled')
            self.rfc_entry.config(state='disabled')
            self.delete_btn.pack_forget()
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Nombre:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = ttk.Entry(main_frame)
        self.nombre_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.telefono_entry = ttk.Entry(main_frame)
        self.telefono_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="RFC:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.rfc_entry = ttk.Entry(main_frame)
        self.rfc_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Barra de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='e', pady=10)
        
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
        
        if self.cliente_id and self.user.perfil != 'cajero':
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_data(self):
        if self.cliente_id:
            self.cliente = self.dao.get(self.cliente_id)
            if self.cliente:
                self.nombre_entry.insert(0, self.cliente.nombre)
                self.telefono_entry.insert(0, self.cliente.telefono)
                self.rfc_entry.insert(0, self.cliente.rfc)
    
    def _get_form_data(self) -> Optional[Cliente]:
        nombre = self.nombre_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        rfc = self.rfc_entry.get().strip().upper()
        
        if not all([nombre, telefono, rfc]):
            self.show_error("Todos los campos son obligatorios")
            return None
            
        return Cliente(
            cliente_id=self.cliente_id,
            usuario_id=self.user.usuario_id,
            nombre=nombre,
            telefono=telefono,
            rfc=rfc
        )
    
    def _save(self):
        cliente = self._get_form_data()
        if not cliente:
            return
            
        if not cliente.validate():
            self.show_error("Datos del cliente no válidos")
            return
            
        if self.cliente_id:
            if self.user.perfil == 'cajero':
                self.show_error("No tiene permisos para editar clientes")
                return
                
            success = self.dao.update(cliente)
            msg = "actualizado"
        else:
            success = self.dao.save(cliente)
            msg = "guardado"
            
        if success:
            self.show_success(f"Cliente {msg} correctamente")
            self.destroy()
        else:
            self.show_error(f"No se pudo {msg} el cliente")
    
    def _delete(self):
        if not self.cliente_id or self.user.perfil == 'cajero':
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este cliente?"):
            if self.dao.delete(self.cliente_id):
                self.show_success("Cliente eliminado correctamente")
                self.destroy()
            else:
                self.show_error("No se pudo eliminar el cliente")