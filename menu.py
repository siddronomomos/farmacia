# menu.py (farmacia)
import tkinter as tk
from tkinter import ttk
from config import Config
from models.user import User

class MenuApp:
    def __init__(self, root: tk.Tk, user: User):
        self.root = root
        self.user = user
        self.root.title(f"{Config.APP_TITLE} - {user.perfil.capitalize()}")
        self.root.geometry("800x500")
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Banner superior
        banner_frame = ttk.Frame(main_frame)
        banner_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(banner_frame, 
                 text=f"Bienvenido, {self.user.nombre}",
                 font=('Arial', 14)).pack(side='left')
        
        ttk.Label(banner_frame, 
                 text=f"Perfil: {self.user.perfil}",
                 font=('Arial', 12)).pack(side='right')
        
        # Botones según perfil
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='both', expand=True)
        
        buttons = []
        
        if self.user.perfil == 'admin':
            buttons.extend([
                ("Usuarios", self._open_users),
                ("Clientes", self._open_clientes),
                ("Proveedores", self._open_proveedores),
                ("Artículos", self._open_articulos),
                ("Ventas", self._open_ventas),
                ("Descuentos", self._open_descuentos),
                ("Compras", self._open_compras),
                ("Reportes", self._open_reportes)
            ])
        elif self.user.perfil == 'gerente':
            buttons.extend([
                ("Clientes", self._open_clientes),
                ("Ventas", self._open_ventas),
                ("Compras", self._open_compras),
                ("Reportes", self._open_reportes)
            ])
        elif self.user.perfil == 'cajero':
            buttons.extend([
                ("Clientes", self._open_clientes),
                ("Ventas", self._open_ventas)
            ])
        
        # Organizar botones en grid
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(buttons_frame, 
                           text=text, 
                           command=command,
                           style='Accent.TButton')
            btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            buttons_frame.rowconfigure(i//3, weight=1)
            buttons_frame.columnconfigure(i%3, weight=1)
        
        # Botón de cierre
        ttk.Button(main_frame, 
                  text="Cerrar Sesión", 
                  command=self._logout).pack(pady=(20, 0))
    
    def _open_users(self):
        from views.frm_user import UserForm
        UserForm(self.root)
    
    def _open_clientes(self):
        from views.frm_cliente import ClienteForm
        ClienteForm(self.root, self.user)
    
    def _open_proveedores(self):
        from views.frm_proveedor import ProveedorForm
        ProveedorForm(self.root)
    
    def _open_articulos(self):
        from views.frm_articulo import ArticuloForm
        ArticuloForm(self.root)
    
    def _open_ventas(self):
        from views.frm_venta import VentaForm
        VentaForm(self.root, self.user)
    
    def _open_compras(self):
        from views.frm_compra import CompraForm
        CompraForm(self.root, self.user)
    
    def _open_descuentos(self):
        from views.frm_descuento import DescuentoForm
        DescuentoForm(self.root)
    
    def _open_reportes(self):
        from views.frm_reporte import ReporteForm
        ReporteForm(self.root)
    
    def _logout(self):
        self.root.destroy()
        from app import App
        App()