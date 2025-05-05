from dataclasses import dataclass
from typing import Optional

@dataclass
class Proveedor:
    proveedor_id: Optional[int] = None
    nombre: Optional[str] = None
    empresa: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    def validate(self) -> bool:
        if not all([self.nombre, self.empresa, self.telefono, self.direccion]):
            return False
        if len(self.nombre) < 3 or len(self.empresa) < 3:
            return False
        if len(self.telefono) < 7 or len(self.direccion) < 5:
            return False
        return True