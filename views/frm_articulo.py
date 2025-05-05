import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.articulo import Articulo
from db.articulo_dao import ArticuloDAO
from views.base_form import BaseForm

class ArticuloForm(BaseForm):
    def __init__(self, parent, articulo_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Artículo", 400, 300)
        self.dao = ArticuloDAO()
        self.articulo = None
        self.articulo_id = articulo_id
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Descripción:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.descripcion_entry = ttk.Entry(main_frame)
        self.descripcion_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Precio Venta:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.precio_entry = ttk.Entry(main_frame)
        self.precio_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Barra de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky='e', pady=10)
        
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
        
        if self.articulo_id:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_data(self):
        if self.articulo_id:
            self.articulo = self.dao.get(self.articulo_id)
            if self.articulo:
                self.descripcion_entry.insert(0, self.articulo.descripcion)
                self.precio_entry.insert(0, str(self.articulo.precio_venta))
    
    def _get_form_data(self) -> Optional[Articulo]:
        descripcion = self.descripcion_entry.get().strip()
        precio_str = self.precio_entry.get().strip()
        
        if not all([descripcion, precio_str]):
            self.show_error("Todos los campos son obligatorios")
            return None
            
        try:
            precio = float(precio_str)
            if precio <= 0:
                self.show_error("El precio debe ser mayor a cero")
                return None
                
            return Articulo(
                articulo_id=self.articulo_id,
                descripcion=descripcion,
                precio_venta=precio
            )
        except ValueError:
            self.show_error("Precio debe ser un número válido")
            return None
    
    def _save(self):
        articulo = self._get_form_data()
        if not articulo:
            return
            
        if not articulo.validate():
            self.show_error("Datos del artículo no válidos")
            return
            
        if self.articulo_id:
            success = self.dao.update(articulo)
            msg = "actualizado"
        else:
            success = self.dao.save(articulo)
            msg = "guardado"
            
        if success:
            self.show_success(f"Artículo {msg} correctamente")
            self.destroy()
        else:
            self.show_error(f"No se pudo {msg} el artículo")
    
    def _delete(self):
        if not self.articulo_id:
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este artículo?"):
            if self.dao.delete(self.articulo_id):
                self.show_success("Artículo eliminado correctamente")
                self.destroy()
            else:
                self.show_error("No se pudo eliminar el artículo")