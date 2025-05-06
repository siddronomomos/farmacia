import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.articulo import Articulo
from db.articulo_dao import ArticuloDAO
from db.proveedor_dao import ProveedorDAO  # Importar DAO de proveedores
from views.base_form import BaseForm

class ArticuloForm(BaseForm):
    def __init__(self, parent, user, articulo_id: Optional[int] = None):
        super().__init__(parent, "Gestión de Artículo", 500, 400)
        self.user = user
        self.dao = ArticuloDAO()
        self.proveedor_dao = ProveedorDAO()
        self.proveedores = self.proveedor_dao.get_all() or []
        if not self.proveedores:
            messagebox.showerror("Error", "No hay proveedores registrados. No se pueden agregar artículos.")
            self.destroy()
            return
        self.articulo = None
        self.articulo_id = articulo_id
        
        self._setup_permissions()
        self._create_widgets()
        self._load_data()
    
    def _setup_permissions(self):
        if self.user.perfil not in ['admin', 'gerente']:
            self.destroy()
            return
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self._search
        ).pack(side='left')
        
        # Campos
        ttk.Label(main_frame, text="Descripción:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.descripcion_entry = ttk.Entry(main_frame)
        self.descripcion_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Precio Venta:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.precio_entry = ttk.Entry(main_frame)
        self.precio_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(main_frame, text="Precio Compra:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.precio_compra_entry = ttk.Entry(main_frame)
        self.precio_compra_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Proveedor:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.proveedor_combobox = ttk.Combobox(main_frame, state="readonly")
        self.proveedor_combobox['values'] = [f"{p.proveedor_id} - {p.nombre}" for p in self.proveedores]
        self.proveedor_combobox.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        # Botones
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
        
        if self.articulo_id:
            self.delete_btn.pack(side='left', padx=5)
    
    def _search(self):
        term = self.search_entry.get().strip()
        if not term:
            return
        
        try:
            # Attempt to search by ID if the term is numeric
            if term.isdigit():
                articulo = self.dao.get_by_id(int(term))
                articulos = [articulo] if articulo else []
            else:
                articulos = self.dao.search(term)
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar artículos: {e}")
            return
        
        if not articulos:
            messagebox.showinfo("Información", "No se encontraron artículos")
            return
            
        # Mostrar resultados en diálogo de selección
        self._show_search_results(articulos)
    
    def _show_search_results(self, articulos):
        dialog = tk.Toplevel(self)
        dialog.title("Resultados de búsqueda")
        
        tree = ttk.Treeview(dialog, columns=('id', 'descripcion', 'precio'), show='headings')
        tree.heading('id', text='ID')
        tree.heading('descripcion', text='Descripción')
        tree.heading('precio', text='Precio')
        
        for art in articulos:
            tree.insert('', 'end', values=(art['articulo_id'], art['descripcion'], art['precio_venta']))
        
        tree.pack(fill='both', expand=True)
        
        def on_select():
            item = tree.focus()
            if item:
                values = tree.item(item, 'values')
                self.articulo_id = int(values[0])
                self._load_data()
                dialog.destroy()
        
        ttk.Button(dialog, text="Seleccionar", command=on_select).pack(pady=5)
    
    def _load_data(self):
        if self.articulo_id:
            self.articulo = self.dao.get_by_id(self.articulo_id)
            if self.articulo:
                self.descripcion_entry.delete(0, tk.END)
                self.descripcion_entry.insert(0, self.articulo['descripcion'])
                self.precio_entry.delete(0, tk.END)
                self.precio_entry.insert(0, str(self.articulo['precio_venta']))
                self.precio_compra_entry.delete(0, tk.END)
                self.precio_compra_entry.insert(0, str(self.articulo['precio_compra']))
                self.proveedor_combobox.set(f"{self.articulo['proveedor_id']} - {self.articulo['proveedor_nombre']}")
    
    def _get_form_data(self) -> Optional[Articulo]:
        descripcion = self.descripcion_entry.get().strip()
        precio_str = self.precio_entry.get().strip()
        precio_compra_str = self.precio_compra_entry.get().strip()
        proveedor = self.proveedor_combobox.get().strip()

        if not all([descripcion, precio_str, precio_compra_str, proveedor]):
            self.show_error("Todos los campos son obligatorios")
            return None
            
        try:
            precio = float(precio_str)
            if precio <= 0:
                self.show_error("El precio debe ser mayor a cero")
                return None

            precio_compra = float(precio_compra_str)
            if precio_compra <= 0:
                self.show_error("El precio de compra debe ser mayor a cero")
                return None

            proveedor_id = int(proveedor.split(" - ")[0])
            return Articulo(
                articulo_id=self.articulo_id,
                descripcion=descripcion,
                precio_venta=precio,
                precio_compra=precio_compra,
                proveedor_id=proveedor_id
            )
        except ValueError:
            self.show_error("Datos inválidos en los campos de precio o proveedor")
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