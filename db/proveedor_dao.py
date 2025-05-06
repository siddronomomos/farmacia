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
            cursor = self.connection.cursor
            cursor.execute(query, params)
            proveedor.proveedor_id = cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar proveedor: {e}")
            self.connection.rollback()
            return False

    def get_all(self):
        query = "SELECT proveedorid AS proveedor_id, nombre, empresa, direccion, telefono FROM proveedor ORDER BY proveedorid"
        rows = self._execute_query(query)
        return [Proveedor(proveedor_id=row['proveedor_id'], nombre=row['nombre'], empresa=row['empresa'], direccion=row['direccion'], telefono=row['telefono']) for row in rows]

    def _execute_query(self, query: str, params: Optional[dict] = None) -> List[dict]:
        cursor = self.connection.cursor
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return rows
        
    def get(self, proveedor_id: int) -> Optional[Proveedor]:
        query = "SELECT * FROM proveedor WHERE proveedorid = %(proveedorid)s"
        params = {'proveedorid': proveedor_id}
        rows = self._execute_query(query, params)
        
        if rows:
            row = rows[0]
            return Proveedor(
                proveedor_id=row['proveedorid'],
                nombre=row['nombre'],
                empresa=row['empresa'],
                direccion=row['direccion'],
                telefono=row['telefono']
            )
        return None