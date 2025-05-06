import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.cliente import Cliente
from models.user import User
from db.cliente_dao import ClienteDAO
from db.user_dao import UserDAO
from views.base_form import BaseForm

class ClienteForm(BaseForm):
    def __init__(self, parent, user: User, cliente_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Cliente", 600, 400)
        self.user = user
        self.cliente_id = cliente_id
        self.cliente_dao = ClienteDAO()
        self.user_dao = UserDAO()
        self.cliente = None
        
        self._create_widgets()
        self._load_data()
        self._setup_permissions()
    
    def _setup_permissions(self):
        """Configura los permisos según el tipo de usuario"""
        if self.user.perfil not in ['admin', 'gerente']:
            # Ocultar campo de usuario para cajeros
            self.usuario_label.grid_remove()
            self.usuario_combo.grid_remove()
            
            # Deshabilitar edición si es un cliente existente
            if self.cliente_id:
                self.nombre_entry.config(state='disabled')
                self.telefono_entry.config(state='disabled')
                self.rfc_entry.config(state='disabled')
                self.delete_btn.pack_forget()
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(search_frame, text="Buscar Cliente por ID:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=10)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self._search_cliente
        ).pack(side='left', padx=5)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = ttk.Entry(main_frame)
        self.nombre_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.telefono_entry = ttk.Entry(main_frame)
        self.telefono_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="RFC:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.rfc_entry = ttk.Entry(main_frame)
        self.rfc_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Combobox para usuario (solo para admin)
        self.usuario_label = ttk.Label(main_frame, text="Usuario:")
        self.usuario_label.grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.usuario_combo = ttk.Combobox(main_frame, state='readonly')
        self.usuario_combo.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        self._load_usuarios()
        
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
        
        ttk.Button(
            button_frame, 
            text="Limpiar", 
            command=self._clear_form
        ).pack(side='left', padx=5)
        
        if self.cliente_id and self.user.perfil in ['admin', 'gerente']:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_usuarios(self):
        """Carga los usuarios en el combobox"""
        usuarios = self.user_dao.get_all()
        self.usuarios = {f"{u.nombre} ({u.user_name})": u.usuario_id for u in usuarios}
        self.usuario_combo['values'] = list(self.usuarios.keys())
        
        # Seleccionar el usuario actual por defecto
        if self.user.perfil in ['admin', 'gerente']:
            usuario_actual = next((k for k, v in self.usuarios.items() if v == self.user.usuario_id), None)
            if usuario_actual:
                self.usuario_combo.set(usuario_actual)
    
    def _search_cliente(self):
        """Busca un cliente por ID con validación de permisos"""
        cliente_id = self.search_entry.get().strip()
        if not cliente_id.isdigit():
            messagebox.showerror("Error", "ID debe ser un número válido")
            return
        
        cliente_id = int(cliente_id)
        cliente = self.cliente_dao.get(cliente_id)
        
        if not cliente:
            messagebox.showerror("Error", f"No se encontró cliente con ID {cliente_id}")
            return
            
        # Para cajeros, verificar que el cliente pertenezca a su usuario
        if self.user.perfil not in ['admin', 'gerente'] and cliente.usuario_id != self.user.usuario_id:
            messagebox.showerror("Error", "Solo puedes ver clientes asignados a tu usuario")
            return
        
        # Cargar datos del cliente encontrado
        self.cliente_id = cliente_id
        self.cliente = cliente
        self._load_cliente_data()
        
        if self.user.perfil in ['admin', 'gerente']:
            self.delete_btn.pack(side='left', padx=5)
        
        messagebox.showinfo("Éxito", f"Cliente {cliente.nombre} cargado correctamente")
    
    def _load_cliente_data(self):
        """Carga los datos del cliente en los campos del formulario"""
        if not self.cliente:
            return
            
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, self.cliente.nombre)
        
        self.telefono_entry.delete(0, tk.END)
        self.telefono_entry.insert(0, self.cliente.telefono)
        
        self.rfc_entry.delete(0, tk.END)
        self.rfc_entry.insert(0, self.cliente.rfc)
        
        # Solo mostrar usuario si es admin o gerente
        if self.user.perfil in ['admin', 'gerente'] and self.cliente.usuario_id:
            usuario = self.user_dao.get(self.cliente.usuario_id)
            if usuario:
                usuario_str = f"{usuario.nombre} ({usuario.user_name})"
                self.usuario_combo.set(usuario_str)
    
    def _load_data(self):
        if self.cliente_id:
            self.cliente = self.cliente_dao.get(self.cliente_id)
            if self.cliente:
                self._load_cliente_data()
    
    def _clear_form(self):
        """Limpia todos los campos del formulario"""
        self.nombre_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.rfc_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        self.usuario_combo.set('')
        
        self.cliente_id = None
        self.cliente = None
        self.delete_btn.pack_forget()
    
    def _get_form_data(self) -> Optional[Cliente]:
        nombre = self.nombre_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        rfc = self.rfc_entry.get().strip().upper()
        
        if self.user.perfil in ['admin', 'gerente']:
            usuario_str = self.usuario_combo.get()
            if not usuario_str:
                self.show_error("Seleccione un usuario")
                return None
            usuario_id = self.usuarios.get(usuario_str)
        else:
            usuario_id = self.user.usuario_id
        
        if not all([nombre, telefono, rfc]):
            self.show_error("Nombre, teléfono y RFC son obligatorios")
            return None
            
        return Cliente(
            cliente_id=self.cliente_id,
            usuario_id=usuario_id,
            nombre=nombre,
            telefono=telefono,
            rfc=rfc
        )
    
    def _save(self):
        cliente = self._get_form_data()
        if not cliente:
            return
            
        if self.cliente_id:
            if self.user.perfil not in ['admin', 'gerente']:
                self.show_error("No tiene permisos para editar clientes")
                return
                
            success = self.cliente_dao.update(cliente)
            msg = "actualizado"
        else:
            success = self.cliente_dao.save(cliente)
            msg = "guardado"
            
        if success:
            self.show_success(f"Cliente {msg} correctamente")
            self._clear_form()
        else:
            self.show_error(f"No se pudo {msg} el cliente")
    
    def _delete(self):
        if not self.cliente_id or self.user.perfil not in ['admin', 'gerente']:
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este cliente?"):
            if self.cliente_dao.delete(self.cliente_id):
                self.show_success("Cliente eliminado correctamente")
                self._clear_form()
            else:
                self.show_error("No se pudo eliminar el cliente")