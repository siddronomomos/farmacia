from typing import List, Optional, Dict
from mysql.connector import Error
from models.venta import Venta
from db.connection import Connection

class VentaDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, venta: Venta) -> bool:
        if not venta.validate():
            return False
            
        query = """
            INSERT INTO ventas (fecha, usuarioid, clienteid)
            VALUES (%(fecha)s, %(usuario_id)s, %(cliente_id)s)
        """
        params = {
            'fecha': venta.fecha,
            'usuario_id': venta.usuario_id,
            'cliente_id': venta.cliente_id
        }
        
        try:
            self.connection.cursor.execute(query, params)
            venta.folio = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar venta: {e}")
            self.connection.rollback()
            return False
    
    def cancel(self, folio: int) -> bool:
        try:
            # Eliminar detalles de venta primero
            query = "DELETE FROM det_venta WHERE folio = %s"
            self.connection.cursor.execute(query, (folio,))
            
            # Luego eliminar la venta
            query = "DELETE FROM ventas WHERE folio = %s"
            self.connection.cursor.execute(query, (folio,))
            
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al cancelar venta: {e}")
            self.connection.rollback()
            return False
    
    def get(self, folio: int) -> Optional[Dict]:
        query = """
            SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
            FROM ventas v
            JOIN clientes c ON v.clienteid = c.clienteid
            JOIN usuarios u ON v.usuarioid = u.usuarioid
            WHERE v.folio = %s
        """
        
        try:
            self.connection.cursor.execute(query, (folio,))
            result = self.connection.cursor.fetchone()
            return result
        except Error as e:
            print(f"Error al obtener venta: {e}")
            return None
    
    def get_all(self) -> List[Dict]:
        query = """
            SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
            FROM ventas v
            JOIN clientes c ON v.clienteid = c.clienteid
            JOIN usuarios u ON v.usuarioid = u.usuarioid
            ORDER BY v.fecha DESC
        """
        
        try:
            self.connection.cursor.execute(query)
            return self.connection.cursor.fetchall()
        except Error as e:
            print(f"Error al obtener ventas: {e}")
            return []