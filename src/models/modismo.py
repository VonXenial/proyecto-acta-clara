from dataclasses import dataclass
from typing import Optional

@dataclass
class ModismoDetectado:
    """
    Clase que representa un modismo chileno detectado en la transcripción.
    Refleja la tabla 'modismos_detectados' de la base de datos SQLite.
    """
    expresion_original: str
    expresion_normalizada: str
    posicion_inicio: int
    posicion_fin: int
    accion_usuario: str  # Puede ser 'ACEPTADA', 'RECHAZADA' o 'EDITADA'
    id: Optional[int] = None
    acta_id: Optional[int] = None
