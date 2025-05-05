from typing import List, Optional, Dict
from mysql.connector import Error
from models.compra import Compra
from db.connection import Connection

class CompraDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, compra: Compra) -> bool:
        if not compra.validate():
            return False
            
        query = """
            INSERT INTO compras (fecha, usuarioid, proveedorid)
            VALUES (%(fecha)s, %(usuario_id)s, %(proveedor_id)s)
        """
        params = {
            'fecha': compra.fecha,
            'usuario_id': compra.usuario_id,
            'proveedor_id': compra.proveedor_id
        }
        
        try:
            self.connection.cursor.execute(query, params)
            compra.folio = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar compra: {e}")
            self.connection.rollback()
            return False
    
    def delete(self, folio: int) -> bool:
        query = "DELETE FROM compras WHERE folio = %s"
        
        try:
            self.connection.cursor.execute(query, (folio,))
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al eliminar compra: {e}")
            self.connection.rollback()
            return False
    
    def get(self, folio: int) -> Optional[Dict]:
        query = """
            SELECT c.*, p.nombre as proveedor_nombre, u.nombre as usuario_nombre
            FROM compras c
            JOIN proveedor p ON c.proveedorid = p.proveedorid
            JOIN usuarios u ON c.usuarioid = u.usuarioid
            WHERE c.folio = %s
        """
        
        try:
            self.connection.cursor.execute(query, (folio,))
            result = self.connection.cursor.fetchone()
            return result
        except Error as e:
            print(f"Error al obtener compra: {e}")
            return None
    
    def get_all(self) -> List[Dict]:
        query = """
            SELECT c.*, p.nombre as proveedor_nombre, u.nombre as usuario_nombre
            FROM compras c
            JOIN proveedor p ON c.proveedorid = p.proveedorid
            JOIN usuarios u ON c.usuarioid = u.usuarioid
            ORDER BY c.fecha DESC
        """
        
        try:
            self.connection.cursor.execute(query)
            return self.connection.cursor.fetchall()
        except Error as e:
            print(f"Error al obtener compras: {e}")
            return []