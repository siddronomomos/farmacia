from dataclasses import dataclass
from typing import Optional, List
from models.proveedor import Proveedor

@dataclass
class Articulo:
    articulo_id: Optional[int]
    descripcion: str
    precio_venta: float
    precio_compra: float
    proveedor_id: int
    proveedor_nombre: Optional[str] = None

    def validate(self) -> bool:
        if self.descripcion is None or len(self.descripcion) < 3:
            return False
        if self.precio_venta is None or self.precio_venta <= 0:
            return False
        return True
