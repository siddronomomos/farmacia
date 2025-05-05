from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Venta:
    folio: Optional[int] = None
    fecha: Optional[date] = None
    usuario_id: Optional[int] = None
    cliente_id: Optional[int] = None

    def validate(self) -> bool:
        if not all([self.fecha, self.usuario_id, self.cliente_id]):
            return False
        
        