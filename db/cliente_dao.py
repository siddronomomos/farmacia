from typing import List, Optional
from mysql.connector import Error
from models.cliente import Cliente
from db.connection import Connection

class ClienteDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, cliente: Cliente) -> bool:
        if not cliente.validate():
            return False
            
        query = """
            INSERT INTO clientes (usuarioid, nombre, telefono, RFC)
            VALUES (%(usuario_id)s, %(nombre)s, %(telefono)s, %(rfc)s)
        """
        params = {
            'usuario_id': cliente.usuario_id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'rfc': cliente.rfc
        }
        
        try:
            self.connection.cursor.execute(query, params)
            cliente.cliente_id = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar cliente: {e}")
            self.connection.rollback()
            return False
    
    def update(self, cliente: Cliente) -> bool:
        if not cliente.validate() or not cliente.cliente_id:
            return False
            
        query = """
            UPDATE clientes
            SET nombre = %(nombre)s,
                telefono = %(telefono)s,
                RFC = %(rfc)s
            WHERE clienteid = %(cliente_id)s
        """
        params = {
            'cliente_id': cliente.cliente_id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'rfc': cliente.rfc
        }
        
        try:
            self.connection.cursor.execute(query, params)
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al actualizar cliente: {e}")
            self.connection.rollback()
            return False
    
    def delete(self, cliente_id: int) -> bool:
        query = "DELETE FROM clientes WHERE clienteid = %s"
        
        try:
            self.connection.cursor.execute(query, (cliente_id,))
            self.connection.commit()
            return self.connection.cursor.rowcount > 0
        except Error as e:
            print(f"Error al eliminar cliente: {e}")
            self.connection.rollback()
            return False
    
    def get(self, cliente_id: int) -> Optional[Cliente]:
        query = "SELECT * FROM clientes WHERE clienteid = %s"
        
        try:
            self.connection.cursor.execute(query, (cliente_id,))
            result = self.connection.cursor.fetchone()
            
            if result:
                return Cliente(
                    cliente_id=result['clienteid'],
                    usuario_id=result['usuarioid'],
                    nombre=result['nombre'],
                    telefono=result['telefono'],
                    rfc=result['RFC']
                )
            return None
        except Error as e:
            print(f"Error al obtener cliente: {e}")
            return None
    
    def get_all(self) -> List[Cliente]:
        query = "SELECT * FROM clientes ORDER BY nombre"
        clientes = []
        
        try:
            self.connection.cursor.execute(query)
            results = self.connection.cursor.fetchall()
            
            for result in results:
                clientes.append(Cliente(
                    cliente_id=result['clienteid'],
                    usuario_id=result['usuarioid'],
                    nombre=result['nombre'],
                    telefono=result['telefono'],
                    rfc=result['RFC']
                ))
            return clientes
        except Error as e:
            print(f"Error al obtener clientes: {e}")
            return []
    
    def search(self, term: str) -> List[Cliente]:
        query = """
            SELECT * FROM clientes 
            WHERE nombre LIKE %s OR telefono LIKE %s OR RFC LIKE %s
            ORDER BY nombre
        """
        term = f"%{term}%"
        clientes = []
        
        try:
            self.connection.cursor.execute(query, (term, term, term))
            results = self.connection.cursor.fetchall()
            
            for result in results:
                clientes.append(Cliente(
                    cliente_id=result['clienteid'],
                    usuario_id=result['usuarioid'],
                    nombre=result['nombre'],
                    telefono=result['telefono'],
                    rfc=result['RFC']
                ))
            return clientes
        except Error as e:
            print(f"Error al buscar clientes: {e}")
            return []