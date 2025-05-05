from dataclasses import dataclass
from typing import Optional

@dataclass
class DescuentoPuntos:
    descuento_id: Optional[int] = None
    puntos_minimos: Optional[int] = None
    puntos_maximos: Optional[int] = None
    porcentaje_descuento: Optional[float] = None

    def validate(self) -> bool:
        if self.puntos_minimos is None or self.puntos_maximos is None or self.porcentaje_descuento is None:
            return False
        if self.puntos_minimos < 0 or self.puntos_maximos < 0 or self.porcentaje_descuento < 0:
            return False
        if self.puntos_minimos >= self.puntos_maximos:
            return False
        if self.porcentaje_descuento > 100 or self.porcentaje_descuento < 0:
            return False
        return True
