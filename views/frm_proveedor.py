# views/frm_proveedor.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.proveedor import Proveedor
from db.proveedor_dao import ProveedorDAO
from views.base_form import BaseForm

class ProveedorForm(BaseForm):
    def __init__(self, parent, user, proveedor_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Proveedor", 500, 350)
        self.user = user
        self._setup_permissions() 
        self.dao = ProveedorDAO()
        self.proveedor = None
        self.proveedor_id = proveedor_id
        
        self._create_widgets()
        self._load_data()
    
    def _setup_permissions(self):
        if self.user.perfil != 'admin':
            self.show_error("No tiene permisos para acceder a esta sección")
            self.destroy()
            return

    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(search_frame, text="Buscar por ID:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=10)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self._search_proveedor
        ).pack(side='left', padx=5)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = ttk.Entry(main_frame)
        self.nombre_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Empresa:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.empresa_entry = ttk.Entry(main_frame)
        self.empresa_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.telefono_entry = ttk.Entry(main_frame)
        self.telefono_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Dirección:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.direccion_entry = ttk.Entry(main_frame)
        self.direccion_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
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
        
        if self.proveedor_id:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_data(self):
        if self.proveedor_id:
            self.proveedor = self.dao.get(self.proveedor_id)
            if self.proveedor:
                self.nombre_entry.insert(0, self.proveedor.nombre)
                self.empresa_entry.insert(0, self.proveedor.empresa)
                self.telefono_entry.insert(0, self.proveedor.telefono)
                self.direccion_entry.insert(0, self.proveedor.direccion)
    
    def _get_form_data(self) -> Optional[Proveedor]:
        nombre = self.nombre_entry.get().strip()
        empresa = self.empresa_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        direccion = self.direccion_entry.get().strip()
        
        if not all([nombre, empresa, telefono, direccion]):
            self.show_error("Todos los campos son obligatorios")
            return None
            
        return Proveedor(
            proveedor_id=self.proveedor_id,
            nombre=nombre,
            empresa=empresa,
            telefono=telefono,
            direccion=direccion
        )
    
    def _save(self):
        proveedor = self._get_form_data()
        if not proveedor:
            return
            
        if not proveedor.validate():
            self.show_error("Datos del proveedor no válidos")
            return
            
        if self.proveedor_id:
            success = self.dao.update(proveedor)
            msg = "actualizado"
        else:
            success = self.dao.save(proveedor)
            msg = "guardado"
            
        if success:
            self.show_success(f"Proveedor {msg} correctamente")
            self.destroy()
        else:
            self.show_error(f"No se pudo {msg} el proveedor")
    
    def _delete(self):
        if not self.proveedor_id:
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este proveedor?"):
            if self.dao.delete(self.proveedor_id):
                self.show_success("Proveedor eliminado correctamente")
                self.destroy()
            else:
                self.show_error("No se pudo eliminar el proveedor")
    
    def _clear_form(self):
        """Limpia todos los campos del formulario"""
        self.nombre_entry.delete(0, tk.END)
        self.empresa_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        
        self.proveedor_id = None
        self.proveedor = None
        self.delete_btn.pack_forget()

    def _search_proveedor(self):
        """Busca un proveedor por ID y carga sus datos"""
        proveedor_id = self.search_entry.get().strip()
        if not proveedor_id.isdigit():
            messagebox.showerror("Error", "ID debe ser un número válido")
            return
        
        proveedor_id = int(proveedor_id)
        proveedor = self.dao.get(proveedor_id)
        if not proveedor:
            messagebox.showerror("Error", f"No se encontró proveedor con ID {proveedor_id}")
            return
        
        # Cargar datos del proveedor encontrado
        self.proveedor_id = proveedor_id
        self.proveedor = proveedor
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, proveedor.nombre)
        self.empresa_entry.delete(0, tk.END)
        self.empresa_entry.insert(0, proveedor.empresa)
        self.telefono_entry.delete(0, tk.END)
        self.telefono_entry.insert(0, proveedor.telefono)
        self.direccion_entry.delete(0, tk.END)
        self.direccion_entry.insert(0, proveedor.direccion)
        
        self.delete_btn.pack(side='left', padx=5)
        messagebox.showinfo("Éxito", f"Proveedor {proveedor.nombre} cargado correctamente")