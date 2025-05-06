from typing import List, Optional
from mysql.connector import Error
from models.descuento_puntos import DescuentoPuntos
from db.connection import Connection

class DescuentoDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, descuento: DescuentoPuntos) -> bool:
        if not descuento.validate():
            return False
            
        query = """
            INSERT INTO descuento_puntos (puntos_minimos, puntos_maximos, porcentaje_descuento)
            VALUES (%(puntos_minimos)s, %(puntos_maximos)s, %(porcentaje_descuento)s)
        """
        params = {
            'puntos_minimos': descuento.puntos_minimos,
            'puntos_maximos': descuento.puntos_maximos,
            'porcentaje_descuento': descuento.porcentaje_descuento
        }
        
        try:
            self.connection.cursor.execute(query, params)
            descuento.descuento_id = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar descuento: {e}")
            self.connection.rollback()
            return False
    
    def get_all(self) -> List[DescuentoPuntos]:
        query = "SELECT * FROM descuento_puntos ORDER BY puntos_minimos"
        descuentos = []
        
        try:
            self.connection.cursor.execute(query)
            results = self.connection.cursor.fetchall()
            
            for result in results:
                descuentos.append(DescuentoPuntos(
                    descuento_id=result['descuentoid'],
                    puntos_minimos=result['puntos_minimos'],
                    puntos_maximos=result['puntos_maximos'],
                    porcentaje_descuento=result['porcentaje_descuento']
                ))
            return descuentos
        except Error as e:
            print(f"Error al obtener descuentos: {e}")
            return []
    
    def get_for_puntos(self, puntos: int) -> List[DescuentoPuntos]:
        query = """
            SELECT * FROM descuento_puntos 
            WHERE %s BETWEEN puntos_minimos AND puntos_maximos
            ORDER BY porcentaje_descuento DESC
        """
        descuentos = []
        
        try:
            self.connection.cursor.execute(query, (puntos,))
            results = self.connection.cursor.fetchall()
            
            for result in results:
                descuentos.append(DescuentoPuntos(
                    descuento_id=result['descuentoid'],
                    puntos_minimos=result['puntos_minimos'],
                    puntos_maximos=result['puntos_maximos'],
                    porcentaje_descuento=result['porcentaje_descuento']
                ))
            return descuentos
        except Error as e:
            print(f"Error al obtener descuentos por puntos: {e}")
            return []
    
    def get(self, descuento_id: int) -> Optional[DescuentoPuntos]:
        query = "SELECT * FROM descuento_puntos WHERE descuentoid = %(descuento_id)s"
        params = {'descuento_id': descuento_id}
        
        try:
            self.connection.cursor.execute(query, params)
            result = self.connection.cursor.fetchone()
            
            if result:
                return DescuentoPuntos(
                    descuento_id=result['descuentoid'],
                    puntos_minimos=result['puntos_minimos'],
                    puntos_maximos=result['puntos_maximos'],
                    porcentaje_descuento=result['porcentaje_descuento']
                )
            return None
        except Error as e:
            print(f"Error al obtener descuento: {e}")
            return None