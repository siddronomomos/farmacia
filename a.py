# create_admin.py
import sys
from db.connection import Connection
from models.user import User
from db.user_dao import UserDAO
import bcrypt

def create_admin_user():
    # Configurar el usuario admin
    admin_user = User(
        nombre="Administrador",
        user_name="admin",
        perfil="admin"
    )
    admin_user.set_password("admin")  # La contraseña se hashea automáticamente
    
    # Verificar si ya existe
    dao = UserDAO()
    existing_admin = dao.get_by_username("admin")
    
    if existing_admin:
        print("El usuario admin ya existe en la base de datos")
        return False
    
    # Crear el usuario
    if dao.save(admin_user):
        print("Usuario admin creado exitosamente!")
        print(f"Username: admin")
        print(f"Password: admin")
        print("\nIMPORTANTE: Cambia la contraseña inmediatamente después del primer login!")
        return True
    else:
        print("Error al crear el usuario admin")
        return False

if __name__ == "__main__":
    print("Creando usuario administrador inicial...")
    if create_admin_user():
        sys.exit(0)
    else:
        sys.exit(1)