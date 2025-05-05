from dataclasses import dataclass
from typing import Optional, List
from datetime import date

@dataclass
class Cliente:
    cliente_id: Optional[int] = None
    usuario_id: Optional[int] = None
    nombre: str = ""
    telefono: str = ""
    rfc: str = ""

    def validate(self) -> bool:
        if not all([self.nombre, self.telefono, self.rfc]):
            return False
        if len(self.telefono) != 10 or not self.telefono.isdigit():
            return False
        if len(self.rfc) not in [10, 13]:
            return False
        return True