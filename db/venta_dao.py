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

    def save_detalle(self, detalle: Dict) -> bool:
        """
        Guarda un detalle de venta en la base de datos.

        :param detalle: Diccionario con los datos del detalle de venta.
        :return: True si se guardó correctamente, False en caso contrario.
        """
        try:
            query = """
                INSERT INTO det_venta (folio, articuloid, cantidad)
                VALUES (%s, %s, %s)
            """  # Corrected: Removed the extra placeholder
            params = (
                detalle['folio'],
                detalle['articulo_id'],
                detalle['cantidad'],
            )
            # Ejecutar la consulta
            self._execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al guardar el detalle de venta: {e}")
            return False
        
    def _execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Ejecuta una consulta SQL y devuelve los resultados.

        :param query: Consulta SQL a ejecutar.
        :param params: Parámetros opcionales para la consulta.
        :return: Lista de diccionarios con los resultados.
        """
        cursor = self.connection.cursor
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def update(self, venta: Venta) -> bool:
        """
        Actualiza una venta existente en la base de datos.

        :param venta: Objeto Venta con los datos actualizados.
        :return: True si se actualizó correctamente, False en caso contrario.
        """
        query = """
            UPDATE ventas
            SET fecha = %(fecha)s, usuarioid = %(usuario_id)s, clienteid = %(cliente_id)s
            WHERE folio = %(folio)s
        """
        params = {
            'fecha': venta.fecha,
            'usuario_id': venta.usuario_id,
            'cliente_id': venta.cliente_id,
            'folio': venta.folio
        }
        
        try:
            self.connection.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al actualizar venta: {e}")
            self.connection.rollback()
            return False

    def get_detalles(self, folio: int) -> List[Dict]:
        """
        Obtiene los detalles de una venta por su folio.

        :param folio: Folio de la venta.
        :return: Lista de diccionarios con los detalles de la venta.
        """
        query = """
            SELECT dv.articuloid, a.descripcion, dv.cantidad, a.precio_venta
            FROM det_venta dv
            JOIN articulos a ON dv.articuloid = a.articuloid
            WHERE dv.folio = %s
        """  # Corrected: Changed 'precio_proveedor' to 'precio_venta'
        
        try:
            self.connection.cursor.execute(query, (folio,))
            return self.connection.cursor.fetchall()
        except Error as e:
            print(f"Error al obtener detalles de la venta: {e}")
            return []

    def update_stock(self, articulo_id: int, cantidad: int) -> bool:
        """
        Actualiza el stock de un artículo.

        :param articulo_id: ID del artículo.
        :param cantidad: Cantidad a sumar/restar del stock.
        :return: True si se actualizó correctamente, False en caso contrario.
        """
        query = """
            UPDATE articulos
            SET existencias = existencias + %s
            WHERE articuloid = %s
        """
        
        try:
            self.connection.cursor.execute(query, (cantidad, articulo_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al actualizar stock: {e}")
            self.connection.rollback()
            return False