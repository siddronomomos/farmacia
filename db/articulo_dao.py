from typing import List, Optional, Dict
from mysql.connector import Error
from models.articulo import Articulo
from db.connection import Connection

class ArticuloDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, articulo: Articulo) -> bool:
        if not articulo.validate():
            return False
            
        query = """
            INSERT INTO articulos (descripcion, precio_venta)
            VALUES (%(descripcion)s, %(precio_venta)s)
        """
        params = {
            'descripcion': articulo.descripcion,
            'precio_venta': articulo.precio_venta
        }
        
        try:
            self.connection.cursor.execute(query, params)
            articulo.articulo_id = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar artículo: {e}")
            self.connection.rollback()
            return False
    
    def update(self, articulo: Articulo) -> bool:
        if not articulo.validate() or not articulo.articulo_id:
            return False
            
        query = """
            UPDATE articulos
            SET descripcion = %(descripcion)s,
                precio_venta = %(precio_venta)s
            WHERE articuloid = %(articulo_id)s
        """
        params = {
            'articulo_id': articulo.articulo_id,
            'descripcion': articulo.descripcion,
            'precio_venta': articulo.precio_venta
        }
        
        try:
            self.connection.cursor.execute(query, params)
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al actualizar artículo: {e}")
            self.connection.rollback()
            return False
    
    def delete(self, articulo_id: int) -> bool:
        query = "DELETE FROM articulos WHERE articuloid = %s"
        
        try:
            self.connection.cursor.execute(query, (articulo_id,))
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al eliminar artículo: {e}")
            self.connection.rollback()
            return False
    
    def get(self, articulo_id: int) -> Optional[Articulo]:
        query = "SELECT * FROM articulos WHERE articuloid = %s"
        
        try:
            self.connection.cursor.execute(query, (articulo_id,))
            result = self.connection.cursor.fetchone()
            
            if result:
                return Articulo(
                    articulo_id=result['articuloid'],
                    descripcion=result['descripcion'],
                    precio_venta=result['precio_venta']
                )
            return None
        except Error as e:
            print(f"Error al obtener artículo: {e}")
            return None
    
    def get_all(self) -> List[Articulo]:
        query = "SELECT * FROM articulos ORDER BY descripcion"
        articulos = []
        
        try:
            self.connection.cursor.execute(query)
            results = self.connection.cursor.fetchall()
            
            for result in results:
                articulos.append(Articulo(
                    articulo_id=result['articuloid'],
                    descripcion=result['descripcion'],
                    precio_venta=result['precio_venta']
                ))
            return articulos
        except Error as e:
            print(f"Error al obtener artículos: {e}")
            return []
    
    def get_by_proveedor(self, proveedor_id: int) -> List[Dict]:
        query = """
            SELECT a.*, da.existencias, da.precio as precio_proveedor
            FROM articulos a
            JOIN det_art da ON a.articuloid = da.articuloid
            WHERE da.proveedorid = %s AND da.existencias > 0
        """
        
        try:
            self.connection.cursor.execute(query, (proveedor_id,))
            results = self.connection.cursor.fetchall()
            return results
        except Error as e:
            print(f"Error al obtener artículos por proveedor: {e}")
            return []
    
    def update_stock(self, articulo_id: int, cantidad: int) -> bool:
        query = """
            UPDATE det_art
            SET existencias = existencias + %s
            WHERE articuloid = %s AND existencias + %s >= 0
        """
        
        try:
            self.connection.cursor.execute(query, (cantidad, articulo_id, cantidad))
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al actualizar stock: {e}")
            self.connection.rollback()
            return False