from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from src.models.modismo import ModismoDetectado

@dataclass
class Acta:
    """
    Clase que representa una reunión transcrita (Acta).
    Refleja la tabla 'actas' de la base de datos SQLite.
    """
    titulo: str
    id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    idioma: str = 'es-CL'
    duracion_segundos: Optional[int] = None
    archivo_audio_ruta: Optional[str] = None
    archivo_docx_ruta: Optional[str] = None
    wer_medido: Optional[float] = None
    version_diccionario: str = '1.0'
    modismos_detectados: Optional[List[ModismoDetectado]] = None
    transcripcion_texto: Optional[str] = None
