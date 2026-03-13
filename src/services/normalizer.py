import json
import re
import logging
from typing import List, Tuple, Dict
from src.models.modismo import ModismoDetectado

# Configurar logger
logger = logging.getLogger("Normalizer")

class Normalizer:
    """
    Servicio para detectar y normalizar modismos chilenos en textos.
    """

    def __init__(self, dictionary_path: str = "data/diccionarios/modismos_es_CL_v1.0.json"):
        """
        Carga el diccionario de modismos desde un archivo JSON.
        """
        self.dictionary_path = dictionary_path
        self.modismos_dict: List[Dict] = []
        self._load_dictionary()

    def _load_dictionary(self):
        """Carga el JSON con los modismos."""
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.modismos_dict = data.get("modismos", [])
            logger.info(f"Diccionario cargado: {len(self.modismos_dict)} modismos encontrados.")
        except Exception as e:
            logger.error(f"Error al cargar el diccionario {self.dictionary_path}: {e}")
            self.modismos_dict = []

    def normalize(self, text: str) -> Tuple[str, List[ModismoDetectado]]:
        """
        Detecta modismos en el texto, los reemplaza por su versión normalizada
        y devuelve una lista de los modismos encontrados con sus posiciones originales.
        """
        if not text:
            return "", []

        modismos_encontrados: List[ModismoDetectado] = []
        
        # Ordenar modismos por longitud de la expresión (descendente) 
        # para evitar problemas de solapamiento (ej: "al tiro que sí" antes que "al tiro")
        sorted_modismos = sorted(self.modismos_dict, key=lambda x: len(x["expresion_original"]), reverse=True)

        normalized_text = text
        
        # Usamos una estrategia de reemplazo que rastrea índices originales
        # Sin embargo, para P2 se solicita detección con Regex y posiciones originales.
        # Es complejo hacer reemplazos múltiples si cambian las longitudes de los strings 
        # manteniendo posiciones "originales" coherentes si se hacen secuencialmente.
        
        # Estrategia: Buscar todos los matches primero sin modificar el texto original.
        matches_info = []
        for modismo in sorted_modismos:
            pattern = r'\b' + re.escape(modismo["expresion_original"]) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Evitar solapamientos: si este rango ya está cubierto, ignorar
                start, end = match.span()
                overlap = any(
                    (start >= m['start'] and start < m['end']) or 
                    (end > m['start'] and end <= m['end']) 
                    for m in matches_info
                )
                
                if not overlap:
                    matches_info.append({
                        'start': start,
                        'end': end,
                        'original': match.group(),
                        'normalizada': modismo['expresion_normalizada'],
                        'modismo_data': modismo
                    })

        # Ordenar matches por posición de inicio para el reemplazo
        matches_info.sort(key=lambda x: x['start'])

        # Crear objetos ModismoDetectado
        for match in matches_info:
            modismos_encontrados.append(
                ModismoDetectado(
                    expresion_original=match['original'],
                    expresion_normalizada=match['normalizada'],
                    posicion_inicio=match['start'],
                    posicion_fin=match['end'],
                    accion_usuario='ACEPTADA' # Valor por defecto inicial
                )
            )

        # Realizar los reemplazos en el texto (de atrás hacia adelante para no romper los índices que quedan)
        temp_text = text
        for match in reversed(matches_info):
            temp_text = temp_text[:match['start']] + match['normalizada'] + temp_text[match['end']:]

        return temp_text, modismos_encontrados
