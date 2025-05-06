# views/frm_reporte.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkinter import filedialog
from db.venta_dao import VentaDAO
from db.compra_dao import CompraDAO
from db.articulo_dao import ArticuloDAO
from views.base_form import BaseForm
import csv

class ReporteForm(BaseForm):
    def __init__(self, parent):
        super().__init__(parent, "Generar Reportes", 600, 400)
        self.venta_dao = VentaDAO()
        self.compra_dao = CompraDAO()
        self.articulo_dao = ArticuloDAO()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = self.create_frame(self)
        main_frame.columnconfigure(1, weight=1)
        
        # Tipo de reporte
        ttk.Label(main_frame, text="Tipo de Reporte:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.tipo_reporte = ttk.Combobox(main_frame, values=[
            "Ventas por período",
            "Compras por período",
            "Artículos más vendidos",
            "Clientes con más compras",
            "Stock bajo"
        ], state='readonly')
        self.tipo_reporte.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.tipo_reporte.current(0)
        
        # Rango de fechas
        self.fecha_frame = ttk.Frame(main_frame)
        self.fecha_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(self.fecha_frame, text="Desde:").pack(side='left', padx=5)
        self.fecha_inicio = ttk.Entry(self.fecha_frame)
        self.fecha_inicio.pack(side='left', padx=5)
        self.fecha_inicio.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        ttk.Label(self.fecha_frame, text="Hasta:").pack(side='left', padx=5)
        self.fecha_fin = ttk.Entry(self.fecha_frame)
        self.fecha_fin.pack(side='left', padx=5)
        self.fecha_fin.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Resultados
        ttk.Label(main_frame, text="Resultados:").grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        self.resultados = tk.Text(main_frame, height=15, width=60)
        self.resultados.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.resultados.yview)
        scrollbar.grid(row=2, column=2, sticky='ns')
        self.resultados.config(yscrollcommand=scrollbar.set)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='e', pady=10)
        
        ttk.Button(
            button_frame, 
            text="Generar", 
            command=self._generar_reporte,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Exportar CSV", 
            command=self._exportar_csv
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cerrar", 
            command=self.destroy
        ).pack(side='left', padx=5)
    
    def _generar_reporte(self):
        tipo = self.tipo_reporte.get()
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        
        try:
            # Validar fechas
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            if fecha_ini > fecha_fin:
                raise ValueError("Fecha inicio debe ser menor que fecha fin")
                
            resultados = ""
            
            if tipo == "Ventas por período":
                ventas = self.venta_dao.get_by_periodo(fecha_inicio, fecha_fin)
                resultados = "Ventas entre {} y {}\n\n".format(fecha_inicio, fecha_fin)
                resultados += "{:<10} {:<15} {:<20} {:<10} {:<10}\n".format(
                    "Folio", "Fecha", "Cliente", "Total", "Puntos"
                )
                resultados += "-"*70 + "\n"
                for v in ventas:
                    resultados += "{:<10} {:<15} {:<20} ${:<9.2f} {:<10}\n".format(
                        v['folio'], 
                        str(v['fecha']), 
                        v['cliente_nombre'][:18], 
                        v['total'], 
                        v.get('puntos', 0)
                    )
                total = sum(v['total'] for v in ventas)
                resultados += "\nTotal de ventas: ${:.2f}".format(total)
                
            elif tipo == "Compras por período":
                compras = self.compra_dao.get_by_periodo(fecha_inicio, fecha_fin)
                resultados = "Compras entre {} y {}\n\n".format(fecha_inicio, fecha_fin)
                resultados += "{:<10} {:<15} {:<20} {:<10}\n".format(
                    "Folio", "Fecha", "Proveedor", "Total"
                )
                resultados += "-"*55 + "\n"
                for c in compras:
                    resultados += "{:<10} {:<15} {:<20} ${:<9.2f}\n".format(
                        c['folio'], 
                        str(c['fecha']), 
                        c['proveedor_nombre'][:18], 
                        c['total']
                    )
                total = sum(c['total'] for c in compras)
                resultados += "\nTotal de compras: ${:.2f}".format(total)
                
            elif tipo == "Artículos más vendidos":
                articulos = self.articulo_dao.get_mas_vendidos(fecha_inicio, fecha_fin)
                resultados = "Artículos más vendidos entre {} y {}\n\n".format(fecha_inicio, fecha_fin)
                resultados += "{:<5} {:<40} {:<10} {:<10}\n".format(
                    "ID", "Descripción", "Vendidos", "Total"
                )
                resultados += "-"*65 + "\n"
                for a in articulos:
                    resultados += "{:<5} {:<40} {:<10} ${:<9.2f}\n".format(
                        a['articulo_id'], 
                        a['descripcion'][:38], 
                        a['cantidad'], 
                        a['total']
                    )
                    
            elif tipo == "Stock bajo":
                articulos = self.articulo_dao.get_stock_bajo()
                resultados = "Artículos con stock bajo\n\n"
                resultados += "{:<5} {:<40} {:<10} {:<10}\n".format(
                    "ID", "Descripción", "Stock", "Proveedor"
                )
                resultados += "-"*65 + "\n"
                for a in articulos:
                    resultados += "{:<5} {:<40} {:<10} {:<10}\n".format(
                        a['articulo_id'], 
                        a['descripcion'][:38], 
                        a['existencias'], 
                        a['proveedor_nombre'][:8]
                    )
            
            self.resultados.delete(1.0, tk.END)
            self.resultados.insert(tk.END, resultados)
            
        except ValueError as e:
            self.show_error(f"Error en fechas: {str(e)}")
        except Exception as e:
            self.show_error(f"Error al generar reporte: {str(e)}")
    
    def _exportar_csv(self):
        contenido = self.resultados.get(1.0, tk.END)
        if not contenido.strip():
            self.show_error("No hay datos para exportar")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Guardar reporte como"
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for line in contenido.split('\n'):
                    # Limpiar y dividir las columnas (asumiendo que están alineadas con espacios)
                    cells = [cell.strip() for cell in line.split('  ') if cell.strip()]
                    writer.writerow(cells)
            
            self.show_success(f"Reporte exportado a {filepath}")
        except Exception as e:
            self.show_error(f"Error al exportar: {str(e)}")