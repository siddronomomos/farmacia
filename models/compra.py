from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Compra:
    folio: Optional[int] = None
    fecha: Optional[date] = None
    usuario_id: Optional[int] = None
    proveedor_id: Optional[int] = None

    def validate(self) -> bool:
        if not all([self.fecha, self.usuario_id, self.proveedor_id]):
            return False
        if self.usuario_id <= 0 or self.proveedor_id <= 0:
            return False
        return True