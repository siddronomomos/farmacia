import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import List, Dict, Optional
from models.venta import Venta
from models.user import User
from db.venta_dao import VentaDAO
from db.cliente_dao import ClienteDAO
from db.articulo_dao import ArticuloDAO
from db.proveedor_dao import ProveedorDAO
from db.descuento_dao import DescuentoDAO
from views.base_form import BaseForm

class VentaForm(BaseForm):
    def __init__(self, parent, user: User):
        super().__init__(parent, "Registro de Venta", 800, 600)
        self.user = user
        self._setup_permissions()
        self.venta_dao = VentaDAO()
        self.cliente_dao = ClienteDAO()
        self.articulo_dao = ArticuloDAO()
        self.proveedor_dao = ProveedorDAO()
        self.descuento_dao = DescuentoDAO()
        
        self.venta = Venta(
            fecha=date.today(),
            usuario_id=user.usuario_id
        )
        self.detalles: List[Dict] = []
        self.articulos_disponibles: List[Dict] = []
        
        self._create_widgets()
        self._load_proveedores()
        self._update_totales()
    
    def _setup_permissions(self):
        # Solo gerente puede cancelar ventas
        if self.user.perfil != 'gerente':
            self.cancel_btn.pack_forget()  # Ocultar botón de cancelación
        
        # Cajero solo puede crear/ver ventas
        if self.user.perfil == 'cajero':
            # Deshabilitar edición de campos si es una venta existente
            if hasattr(self, 'venta_id') and self.venta_id:
                self._disable_edition()
    
    def _disable_edition(self):
        """Deshabilita la edición para usuarios con permisos limitados"""
        self.cliente_search.config(state='disabled')
        self.proveedor_combo.config(state='disabled')
        self.articulo_combo.config(state='disabled')
        self.cantidad_entry.config(state='disabled')
        self.agregar_btn.config(state='disabled')
        self.quitar_btn.config(state='disabled')
        self.limpiar_btn.config(state='disabled')
        self.descuento_combo.config(state='disabled')
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Frame de búsqueda de cliente
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(search_frame, text="Buscar Cliente:").pack(side='left', padx=5)
        self.cliente_search = ttk.Entry(search_frame, width=30)
        self.cliente_search.pack(side='left', padx=5)
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self._search_cliente
        ).pack(side='left', padx=5)
        
        # Info del cliente seleccionado
        self.cliente_info = ttk.Label(main_frame, text="Cliente: No seleccionado")
        self.cliente_info.grid(row=1, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        
        # Frame de selección de artículos
        articulo_frame = ttk.Frame(main_frame)
        articulo_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(articulo_frame, text="Proveedor:").pack(side='left', padx=5)
        self.proveedor_combo = ttk.Combobox(articulo_frame, state='readonly')
        self.proveedor_combo.pack(side='left', padx=5)
        self.proveedor_combo.bind('<<ComboboxSelected>>', self._load_articulos_proveedor)
        
        ttk.Label(articulo_frame, text="Artículo:").pack(side='left', padx=5)
        self.articulo_combo = ttk.Combobox(articulo_frame, state='readonly')
        self.articulo_combo.pack(side='left', padx=5)
        
        ttk.Label(articulo_frame, text="Cantidad:").pack(side='left', padx=5)
        self.cantidad_entry = ttk.Entry(articulo_frame, width=5)
        self.cantidad_entry.pack(side='left', padx=5)
        self.cantidad_entry.insert(0, "1")
        
        self.agregar_btn = ttk.Button(
            articulo_frame, 
            text="Agregar", 
            command=self._agregar_articulo
        )
        self.agregar_btn.pack(side='left', padx=5)
        
        # Lista de artículos agregados
        self.articulos_listbox = tk.Listbox(main_frame, height=10)
        self.articulos_listbox.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.articulos_listbox.yview)
        scrollbar.grid(row=3, column=2, sticky='ns')
        self.articulos_listbox.config(yscrollcommand=scrollbar.set)
        
        # Botones para manejar lista de artículos
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=5)
        
        self.quitar_btn = ttk.Button(
            button_frame, 
            text="Quitar Artículo", 
            command=self._quitar_articulo
        )
        self.quitar_btn.pack(side='left', padx=5)
        
        self.limpiar_btn = ttk.Button(
            button_frame, 
            text="Limpiar Lista", 
            command=self._limpiar_lista
        )
        self.limpiar_btn.pack(side='left', padx=5)
        
        # Frame de totales y descuentos
        total_frame = ttk.Frame(main_frame)
        total_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(total_frame, text="Descuento:").pack(side='left', padx=5)
        self.descuento_combo = ttk.Combobox(total_frame, state='readonly')
        self.descuento_combo.pack(side='left', padx=5)
        self.descuento_combo.bind('<<ComboboxSelected>>', self._aplicar_descuento)
        
        ttk.Label(total_frame, text="Subtotal:").pack(side='left', padx=5)
        self.subtotal_label = ttk.Label(total_frame, text="$0.00")
        self.subtotal_label.pack(side='left', padx=5)
        
        ttk.Label(total_frame, text="IVA (16%):").pack(side='left', padx=5)
        self.iva_label = ttk.Label(total_frame, text="$0.00")
        self.iva_label.pack(side='left', padx=5)
        
        ttk.Label(total_frame, text="Total:").pack(side='left', padx=5)
        self.total_label = ttk.Label(total_frame, text="$0.00", font=('Arial', 10, 'bold'))
        self.total_label.pack(side='left', padx=5)
        
        # Botones finales
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=6, column=0, columnspan=3, sticky='e', pady=10)
        
        ttk.Button(
            action_frame, 
            text="Cancelar", 
            command=self.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame, 
            text="Registrar Venta", 
            command=self._registrar_venta,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
    
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
        self.articulos_disponibles = self.articulo_dao.get_by_proveedor(proveedor_id)
        
        self.articulo_combo['values'] = [
            f"{a['articuloid']} - {a['descripcion']} (${a['precio_proveedor']:.2f}) - Stock: {a['existencias']}" 
            for a in self.articulos_disponibles
        ]
        
        if self.articulos_disponibles:
            self.articulo_combo.current(0)
    
    def _search_cliente(self):
        query = self.cliente_search.get().strip()
        if not query:
            return
            
        clientes = self.cliente_dao.search(query)
        if not clientes:
            messagebox.showinfo("Información", "No se encontraron clientes con ese criterio")
            return
            
        # Mostrar diálogo de selección
        seleccion = self._mostrar_seleccion_clientes(clientes)
        if seleccion:
            self.venta.cliente_id = seleccion.cliente_id
            self.cliente_info.config(text=f"Cliente: {seleccion.nombre} - Tel: {seleccion.telefono} - RFC: {seleccion.rfc}")
            self._update_totales()
    
    def _mostrar_seleccion_clientes(self, clientes):
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar Cliente")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Crear Treeview
        columns = ('nombre', 'telefono', 'rfc')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Configurar columnas
        tree.heading('nombre', text='Nombre')
        tree.heading('telefono', text='Teléfono')
        tree.heading('rfc', text='RFC')
        
        tree.column('nombre', width=150)
        tree.column('telefono', width=100)
        tree.column('rfc', width=120)
        
        # Agregar datos
        for cliente in clientes:
            tree.insert('', 'end', values=(cliente.nombre, cliente.telefono, cliente.rfc))
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        selected_cliente = None
        
        def on_select():
            nonlocal selected_cliente
            item = tree.focus()
            if item:
                values = tree.item(item, 'values')
                selected_cliente = next((c for c in clientes if c.rfc == values[2]), None)
                dialog.destroy()
        
        ttk.Button(
            dialog, 
            text="Seleccionar", 
            command=on_select
        ).pack(pady=5)
        
        self.wait_window(dialog)
        return selected_cliente
    
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
        articulo = next((a for a in self.articulos_disponibles if a['articuloid'] == articulo_id), None)
        
        if not articulo:
            messagebox.showerror("Error", "Artículo no encontrado")
            return
            
        if cantidad > articulo['existencias']:
            messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {articulo['existencias']}")
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
                'descripcion': articulo['descripcion'],
                'cantidad': cantidad,
                'precio_unitario': articulo['precio_proveedor']
            })
        
        # Actualizar lista y totales
        self._actualizar_lista_articulos()
        self._update_totales()
        
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
        self._update_totales()
    
    def _limpiar_lista(self):
        if self.detalles and not messagebox.askyesno("Confirmar", "¿Está seguro de limpiar la lista de artículos?"):
            return
            
        self.detalles = []
        self._actualizar_lista_articulos()
        self._update_totales()
    
    def _actualizar_lista_articulos(self):
        self.articulos_listbox.delete(0, tk.END)
        
        for detalle in self.detalles:
            texto = f"{detalle['articulo_id']} - {detalle['descripcion']} x{detalle['cantidad']} (${detalle['precio_unitario']:.2f} c/u)"
            self.articulos_listbox.insert(tk.END, texto)
    
    def _update_totales(self):
        subtotal = sum(d['cantidad'] * d['precio_unitario'] for d in self.detalles)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        self.venta.subtotal = subtotal
        self.venta.iva = iva
        self.venta.total = total
        
        self.subtotal_label.config(text=f"${subtotal:.2f}")
        self.iva_label.config(text=f"${iva:.2f}")
        self.total_label.config(text=f"${total:.2f}")
        
        # Actualizar descuentos disponibles si hay cliente
        if self.venta.cliente_id:
            cliente = self.cliente_dao.get(self.venta.cliente_id)
            if cliente and hasattr(cliente, 'puntos'):
                descuentos = self.descuento_dao.get_for_puntos(cliente.puntos)
                
                self.descuento_combo['values'] = [
                    f"{d.porcentaje_descuento}% (requiere {d.puntos_minimos}-{d.puntos_maximos} puntos)"
                    for d in descuentos
                ]
                
                if descuentos:
                    self.descuento_combo.current(0)
                    self._aplicar_descuento()
    
    def _aplicar_descuento(self, event=None):
        if not self.detalles:
            return
            
        descuento_str = self.descuento_combo.get()
        if not descuento_str:
            self._update_totales()  # Resetear a valores sin descuento
            return
            
        try:
            porcentaje = float(descuento_str.split('%')[0])
            descuento = self.venta.subtotal * (porcentaje / 100)
            
            subtotal = self.venta.subtotal
            iva = (subtotal - descuento) * 0.16
            total = (subtotal - descuento) + iva
            
            self.subtotal_label.config(text=f"${subtotal:.2f} (-${descuento:.2f})")
            self.iva_label.config(text=f"${iva:.2f}")
            self.total_label.config(text=f"${total:.2f}", font=('Arial', 10, 'bold'))
            
            # Guardar el descuento aplicado
            descuentos = self.descuento_dao.get_all()
            selected = next(
                (d for d in descuentos if f"{d.porcentaje_descuento}%" in descuento_str),
                None
            )
            self.venta.descuento_id = selected.descuento_id if selected else None
        except:
            self._update_totales()
    
    def _registrar_venta(self):
        if not self.venta.cliente_id:
            messagebox.showerror("Error", "Seleccione un cliente")
            return
            
        if not self.detalles:
            messagebox.showerror("Error", "Agregue al menos un artículo")
            return
            
        # Confirmar la venta
        if not messagebox.askyesno("Confirmar", "¿Registrar la venta?"):
            return
            
        # Calcular puntos (1 punto por cada 10 centavos, sin contar descuentos)
        self.venta.puntos = int(self.venta.subtotal * 10)
        
        try:
            # Registrar la venta
            if not self.venta_dao.save(self.venta):
                raise Exception("No se pudo guardar la venta")
            
            # Registrar los detalles
            for detalle in self.detalles:
                det = {
                    'folio': self.venta.folio,
                    'articulo_id': detalle['articulo_id'],
                    'cantidad': detalle['cantidad'],
                    'precio_unitario': detalle['precio_unitario']
                }
                
                if not self.venta_dao.save_detalle(det):
                    raise Exception("No se pudo guardar el detalle de venta")
                
                # Actualizar stock
                if not self.articulo_dao.update_stock(det['articulo_id'], -det['cantidad']):
                    raise Exception("No se pudo actualizar el stock")
            
            messagebox.showinfo("Éxito", f"Venta registrada con folio: {self.venta.folio}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar la venta: {str(e)}")