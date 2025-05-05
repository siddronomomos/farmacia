from typing import List, Optional
from mysql.connector import Error
from models.proveedor import Proveedor
from db.connection import Connection

class ProveedorDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, proveedor: Proveedor) -> bool:
        if not proveedor.validate():
            return False
            
        query = """
            INSERT INTO proveedor (nombre, empresa, direccion, telefono)
            VALUES (%(nombre)s, %(empresa)s, %(direccion)s, %(telefono)s)
        """
        params = {
            'nombre': proveedor.nombre,
            'empresa': proveedor.empresa,
            'direccion': proveedor.direccion,
            'telefono': proveedor.telefono
        }
        
        try:
            self.connection.cursor.execute(query, params)
            proveedor.proveedor_id = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar proveedor: {e}")
            self.connection.rollback()
            return False
    
    def get_all(self) -> List[Proveedor]:
        query = "SELECT * FROM proveedor ORDER BY nombre"
        proveedores = []
        
        try:
            self.connection.cursor.execute(query)
            results = self.connection.cursor.fetchall()
            
            for result in results:
                proveedores.append(Proveedor(
                    proveedor_id=result['proveedorid'],
                    nombre=result['nombre'],
                    empresa=result['empresa'],
                    direccion=result['direccion'],
                    telefono=result['telefono']
                ))
            return proveedores
        except Error as e:
            print(f"Error al obtener proveedores: {e}")
            return []