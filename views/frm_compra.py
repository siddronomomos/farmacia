import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import List, Dict, Optional
from models.compra import Compra
from models.user import User
from db.compra_dao import CompraDAO
from db.proveedor_dao import ProveedorDAO
from db.articulo_dao import ArticuloDAO
from views.base_form import BaseForm

class CompraForm(BaseForm):
    def __init__(self, parent, user: User, folio: Optional[int] = None):
        super().__init__(parent, "Registro de Compra", 700, 500)
        self.user = user
        self.compra_dao = CompraDAO()
        self.proveedor_dao = ProveedorDAO()
        self.articulo_dao = ArticuloDAO()
        self.compra = None
        self.folio = folio
        self.detalles: List[Dict] = []
        
        self._create_widgets()
        self._load_proveedores()
        self._load_data()
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Proveedor
        ttk.Label(main_frame, text="Proveedor:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.proveedor_combo = ttk.Combobox(main_frame, state='readonly')
        self.proveedor_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Artículos
        ttk.Label(main_frame, text="Artículo:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.articulo_combo = ttk.Combobox(main_frame, state='readonly')
        self.articulo_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Cantidad:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.cantidad_entry = ttk.Entry(main_frame)
        self.cantidad_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        self.cantidad_entry.insert(0, "1")
        
        ttk.Button(
            main_frame, 
            text="Agregar Artículo", 
            command=self._agregar_articulo
        ).grid(row=3, column=1, sticky='e', pady=5)
        
        # Lista de artículos
        self.articulos_listbox = tk.Listbox(main_frame, height=10)
        self.articulos_listbox.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.articulos_listbox.yview)
        scrollbar.grid(row=4, column=2, sticky='ns')
        self.articulos_listbox.config(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky='e', pady=10)
        
        self.delete_btn = ttk.Button(
            button_frame, 
            text="Eliminar Compra", 
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
        
        if self.folio:
            self.delete_btn.pack(side='left', padx=5)
    
    def _load_proveedores(self):
        proveedores = self.proveedor_dao.get_all()
        self.proveedores = {f"{p.nombre} - {p.empresa}": p.proveedor_id for p in proveedores}
        self.proveedor_combo['values'] = list(self.proveedores.keys())
        
        if proveedores:
            self.proveedor_combo.current(0)
            self._load_articulos_proveedor()
    
    def _load_articulos_proveedor(self, event=None):
        proveedor_str = self.proveedor_combo.get()
        if not proveedor_str:
            return
            
        proveedor_id = self.proveedores[proveedor_str]
        articulos = self.articulo_dao.get_all()
        
        self.articulo_combo['values'] = [
            f"{a.articulo_id} - {a.descripcion} (${a.precio_venta:.2f})" 
            for a in articulos
        ]
        
        if articulos:
            self.articulo_combo.current(0)
    
    def _agregar_articulo(self):
        articulo_str = self.articulo_combo.get()
        cantidad_str = self.cantidad_entry.get()
        
        if not articulo_str or not cantidad_str.isdigit():
            messagebox.showerror("Error", "Seleccione un artículo y cantidad válida")
            return
            
        cantidad = int(cantidad_str)
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a cero")
            return
            
        # Obtener artículo seleccionado
        articulo_id = int(articulo_str.split(' - ')[0])
        articulo = self.articulo_dao.get(articulo_id)
        
        if not articulo:
            messagebox.showerror("Error", "Artículo no encontrado")
            return
            
        # Verificar si ya está en la lista
        detalle_existente = next((d for d in self.detalles if d['articulo_id'] == articulo_id), None)
        
        if detalle_existente:
            # Actualizar cantidad
            detalle_existente['cantidad'] += cantidad
        else:
            # Agregar nuevo detalle
            self.detalles.append({
                'articulo_id': articulo_id,
                'descripcion': articulo.descripcion,
                'cantidad': cantidad,
                'precio_unitario': articulo.precio_venta
            })
        
        # Actualizar lista
        self._actualizar_lista_articulos()
        
        # Limpiar cantidad
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
    
    def _quitar_articulo(self):
        seleccion = self.articulos_listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para quitar")
            return
            
        index = seleccion[0]
        self.detalles.pop(index)
        self._actualizar_lista_articulos()
    
    def _actualizar_lista_articulos(self):
        self.articulos_listbox.delete(0, tk.END)
        
        for detalle in self.detalles:
            texto = f"{detalle['articulo_id']} - {detalle['descripcion']} x{detalle['cantidad']}"
            self.articulos_listbox.insert(tk.END, texto)
    
    def _load_data(self):
        if self.folio:
            self.compra = self.compra_dao.get(self.folio)
            if self.compra:
                # Configurar proveedor
                proveedor_str = f"{self.compra['proveedor_nombre']} - {self.compra['empresa']}"
                self.proveedor_combo.set(proveedor_str)
                
                # Cargar detalles
                detalles = self.compra_dao.get_detalles(self.folio)
                for detalle in detalles:
                    self.detalles.append({
                        'articulo_id': detalle['articuloid'],
                        'descripcion': detalle['descripcion'],
                        'cantidad': detalle['cantidad'],
                        'precio_unitario': detalle['precio_venta']
                    })
                
                self._actualizar_lista_articulos()
    
    def _get_form_data(self) -> Optional[Compra]:
        proveedor_str = self.proveedor_combo.get()
        if not proveedor_str:
            self.show_error("Seleccione un proveedor")
            return None
            
        if not self.detalles:
            self.show_error("Agregue al menos un artículo")
            return None
            
        proveedor_id = self.proveedores[proveedor_str]
        
        return Compra(
            folio=self.folio,
            fecha=date.today(),
            usuario_id=self.user.usuario_id,
            proveedor_id=proveedor_id
        )
    
    def _save(self):
        compra = self._get_form_data()
        if not compra:
            return
            
        if self.folio:
            # Actualizar compra existente
            if not self.compra_dao.update(compra):
                self.show_error("No se pudo actualizar la compra")
                return
                
            # Eliminar detalles antiguos
            self.compra_dao.delete_detalles(compra.folio)
        else:
            # Crear nueva compra
            if not self.compra_dao.save(compra):
                self.show_error("No se pudo guardar la compra")
                return
        
        # Guardar detalles
        for detalle in self.detalles:
            if not self.compra_dao.save_detalle(compra.folio, detalle):
                self.show_error("Error al guardar detalles de compra")
                return
            
            # Actualizar stock
            if not self.articulo_dao.update_stock(detalle['articulo_id'], detalle['cantidad']):
                self.show_error("Error al actualizar stock")
                return
        
        self.show_success(f"Compra {'actualizada' if self.folio else 'registrada'} correctamente")
        self.destroy()
    
    def _delete(self):
        if not self.folio:
            return
            
        if not self.ask_confirmation("¿Está seguro de eliminar esta compra?"):
            return
            
        if self.compra_dao.delete(self.folio):
            self.show_success("Compra eliminada correctamente")
            self.destroy()
        else:
            self.show_error("No se pudo eliminar la compra")