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
            
        try:
            # Insert into articulos table
            query_articulos = """
                INSERT INTO articulos (descripcion, precio_venta)
                VALUES (%s, %s)
            """
            params_articulos = (articulo.descripcion, articulo.precio_venta)
            self.connection.cursor.execute(query_articulos, params_articulos)
            articulo.articulo_id = self.connection.cursor.lastrowid

            # Insert into det_art table
            query_det_art = """
                INSERT INTO det_art (proveedorid, articuloid, precio, existencias)
                VALUES (%s, %s, %s, 0)
            """
            params_det_art = (articulo.proveedor_id, articulo.articulo_id, articulo.precio_compra)
            self.connection.cursor.execute(query_det_art, params_det_art)

            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar artículo: {e}")
            self.connection.rollback()
            return False
    
    def update(self, articulo: Articulo) -> bool:
        if not articulo.validate() or not articulo.articulo_id:
            return False
            
        try:
            # Update articulos table
            query_articulos = """
                UPDATE articulos
                SET descripcion = %s, precio_venta = %s
                WHERE articuloid = %s
            """
            params_articulos = (articulo.descripcion, articulo.precio_venta, articulo.articulo_id)
            self.connection.cursor.execute(query_articulos, params_articulos)

            # Update det_art table
            query_det_art = """
                UPDATE det_art
                SET precio = %s, proveedorid = %s
                WHERE articuloid = %s
            """
            params_det_art = (articulo.precio_compra, articulo.proveedor_id, articulo.articulo_id)
            self.connection.cursor.execute(query_det_art, params_det_art)

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
        query = """
            SELECT a.articuloid, a.descripcion, a.precio_venta, a.precio_compra, a.proveedor_id, p.nombre
            FROM articulos a
            JOIN proveedor p ON a.proveedor_id = p.proveedor_id
            WHERE a.articuloid = %s
        """
        
        try:
            self.connection.cursor.execute(query, (articulo_id,))
            result = self.connection.cursor.fetchone()
            
            if result:
                return Articulo(
                    articulo_id=result['articuloid'],
                    descripcion=result['descripcion'],
                    precio_venta=result['precio_venta'],
                    precio_compra=result['precio_compra'],
                    proveedor_id=result['proveedor_id'],
                    proveedor_nombre=result['nombre']
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
                    precio_venta=result['precio_venta'],
                    precio_compra=result['precio_compra'],
                    proveedor_id=result['proveedor_id']
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

    def search(self, term: str):
        query = """
            SELECT a.articuloid AS articulo_id, a.descripcion, a.precio_venta, da.precio AS precio_compra
            FROM articulos a
            LEFT JOIN det_art da ON a.articuloid = da.articuloid
            WHERE a.descripcion LIKE %(term)s
        """
        params = {'term': f"%{term}%"}
        cursor = self.connection.cursor
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                'articulo_id': row['articulo_id'],
                'descripcion': row['descripcion'],
                'precio_venta': row['precio_venta'],
                'precio_compra': row['precio_compra']
            }
            for row in rows
        ]

    def get_by_id(self, articulo_id: int):
        query = """
            SELECT a.articuloid AS articulo_id, a.descripcion, a.precio_venta, 
                   da.precio AS precio_compra, da.proveedorid, p.nombre AS proveedor_nombre
            FROM articulos a
            LEFT JOIN det_art da ON a.articuloid = da.articuloid
            LEFT JOIN proveedor p ON da.proveedorid = p.proveedorid
            WHERE a.articuloid = %(articulo_id)s
        """
        params = {'articulo_id': articulo_id}
        cursor = self.connection.cursor
        cursor.execute(query, params)
        row = cursor.fetchone()
        return {
            'articulo_id': row['articulo_id'],
            'descripcion': row['descripcion'],
            'precio_venta': row['precio_venta'],
            'precio_compra': row['precio_compra'],
            'proveedor_id': row['proveedorid'],
            'proveedor_nombre': row['proveedor_nombre']
        } if row else None