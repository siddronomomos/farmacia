from dataclasses import dataclass
from typing import Optional, Literal

PerfilType = Literal["admin", "cajero", "gerente"]

@dataclass
class User:
    usuario_id: Optional[int] = None
    nombre: Optional[str] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    perfil: Optional[PerfilType] = None

    def validate(self) -> bool:
        if not all([self.nombre, self.user_name, self.password, self.perfil]):
            return False
        if len(self.user_name) < 3 or len(self.user_name) > 20:
            return False
        if self.perfil not in ["admin", "cajero", "gerente"]:
            return False
        return True
    
    def set_password(self, password: str) -> None:
        import bcrypt
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        import bcrypt
        try:
            if not self.password or not isinstance(self.password, str):
                return False
                
            if not self.password.startswith('$2b$'):
                print(f"Hash inválido: {self.password}")
                return False
                
            return bcrypt.checkpw(password.encode(), self.password.encode())
        except Exception as e:
            print(f"Error en check_password: {str(e)}")
            return False
    
    def __str__(self):
        return f"{self.nombre} ({self.perfil})"

