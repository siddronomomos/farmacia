from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Articulo:
    articulo_id: Optional[int] = None
    descripcion: Optional[str] = None
    precio_venta: Optional[float] = None

    def validate(self) -> bool:
        if self.descripcion is None or len(self.descripcion) < 3:
            return False
        if self.precio_venta is None or self.precio_venta <= 0:
            return False
        return True
