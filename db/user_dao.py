from typing import List, Optional
from mysql.connector import Error
from models.user import User
from db.connection import Connection

class UserDAO:
    def __init__(self):
        self.connection = Connection()
    
    def save(self, user: User) -> bool:
        if not user.validate():
            return False
            
        query = """
            INSERT INTO usuarios (nombre, password, perfil)
            VALUES (%(nombre)s, %(password)s, %(perfil)s)
        """
        params = {
            'nombre': user.nombre,
            'password': user.password,
            'perfil': user.perfil
        }
        
        try:
            self.connection.cursor.execute(query, params)
            user.usuario_id = self.connection.cursor.lastrowid
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al guardar usuario: {e}")
            self.connection.rollback()
            return False
    
    def get_by_username(self, username: str) -> Optional[User]:
        query = "SELECT * FROM usuarios WHERE user_name = %s"
        
        try:
            self.connection.cursor.execute(query, (username,))
            result = self.connection.cursor.fetchone()
            
            if result:
                return User(
                    usuario_id=result['usuarioid'],
                    nombre=result['nombre'],
                    user_name=result['user_name'],
                    password=result['password'],
                    perfil=result['perfil']
                )
            return None
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            return None