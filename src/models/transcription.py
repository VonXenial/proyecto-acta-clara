from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TranscripcionSegmento:
    """Representa un segmento de texto transcrito con sus marcas de tiempo."""
    texto: str
    inicio: float
    fin: float

@dataclass
class Transcription:
    """
    Clase que engloba el resultado de la transcripción de un archivo de audio,
    utilizada en la lógica de negocio antes de la persistencia como un Acta.
    """
    texto_completo: str
    segmentos: List[TranscripcionSegmento] = field(default_factory=list)
    idioma_detectado: Optional[str] = None
    duracion_procesada: Optional[float] = None
