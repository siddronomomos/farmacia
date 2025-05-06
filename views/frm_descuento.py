# views/frm_descuento.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.descuento_puntos import DescuentoPuntos
from db.descuento_dao import DescuentoDAO
from views.base_form import BaseForm

class DescuentoForm(BaseForm):
    def __init__(self, parent, user, descuento_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Descuento", 400, 250)
        self.user = user
        self._setup_permissions()
        self.dao = DescuentoDAO()
        self.descuento = None
        self.descuento_id = descuento_id
        
        self._create_widgets()
        self._load_data()
    
    def _setup_permissions(self):
        # Solo admin puede gestionar descuentos
        if self.user.perfil != 'admin':
            self.destroy()
            return
        
        # Si es gerente o cajero, solo lectura
        if self.user.perfil in ['gerente', 'cajero'] and self.descuento_id:
            self.min_entry.config(state='readonly')
            self.max_entry.config(state='readonly')
            self.porcentaje_entry.config(state='readonly')
            self.delete_btn.pack_forget()

    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Puntos Mínimos:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.min_entry = ttk.Entry(main_frame)
        self.min_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Puntos Máximos:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.max_entry = ttk.Entry(main_frame)
        self.max_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="% Descuento:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.porcentaje_entry = ttk.Entry(main_frame)
        self.porcentaje_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
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
        
        if self.descuento_id:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_data(self):
        if self.descuento_id:
            self.descuento = self.dao.get(self.descuento_id)
            if self.descuento:
                self.min_entry.insert(0, str(self.descuento.puntos_minimos))
                self.max_entry.insert(0, str(self.descuento.puntos_maximos))
                self.porcentaje_entry.insert(0, str(self.descuento.porcentaje_descuento))
    
    def _get_form_data(self) -> Optional[DescuentoPuntos]:
        try:
            min_puntos = int(self.min_entry.get().strip())
            max_puntos = int(self.max_entry.get().strip())
            porcentaje = float(self.porcentaje_entry.get().strip())
            
            return DescuentoPuntos(
                descuento_id=self.descuento_id,
                puntos_minimos=min_puntos,
                puntos_maximos=max_puntos,
                porcentaje_descuento=porcentaje
            )
        except ValueError:
            self.show_error("Todos los campos deben ser números válidos")
            return None
    
    def _save(self):
        descuento = self._get_form_data()
        if not descuento:
            return
            
        if not descuento.validate():
            self.show_error("Datos del descuento no válidos")
            return
            
        if self.descuento_id:
            success = self.dao.update(descuento)
            msg = "actualizado"
        else:
            success = self.dao.save(descuento)
            msg = "guardado"
            
        if success:
            self.show_success(f"Descuento {msg} correctamente")
            self.destroy()
        else:
            self.show_error(f"No se pudo {msg} el descuento")
    
    def _delete(self):
        if not self.descuento_id:
            return
            
        if self.ask_confirmation("¿Está seguro de eliminar este descuento?"):
            if self.dao.delete(self.descuento_id):
                self.show_success("Descuento eliminado correctamente")
                self.destroy()
            else:
                self.show_error("No se pudo eliminar el descuento")