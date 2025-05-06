# models/venta.py
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import date

@dataclass
class Venta:
    folio: Optional[int] = None
    fecha: Optional[date] = None
    usuario_id: Optional[int] = None
    cliente_id: Optional[int] = None
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    puntos: int = 0
    descuento_id: Optional[int] = None

    def validate(self) -> bool:
        if not all([self.fecha, self.usuario_id, self.cliente_id]):
            return False
        if self.total <= 0:
            return False
        return True