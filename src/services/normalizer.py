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

    def add_new_idiom(self, original: str, normalizada: str):
        """Agrega un nuevo modismo al diccionario y lo persiste en el JSON."""
        # Verificar si ya existe
        for mod in self.modismos_dict:
            if mod["expresion_original"].lower() == original.lower():
                mod["expresion_normalizada"] = normalizada
                self._save_dictionary()
                return

        # Crear nuevo
        new_id = f"custom_{len(self.modismos_dict) + 1:03d}"
        self.modismos_dict.append({
            "id": new_id,
            "expresion_original": original,
            "expresion_normalizada": normalizada,
            "categoria": "usuario",
            "frecuencia": "alta"
        })
        self._save_dictionary()

    def _save_dictionary(self):
        """Guarda el estado actual del diccionario en el archivo JSON."""
        try:
            # Leer el archivo completo para mantener la estructura metadata
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            full_data["modismos"] = self.modismos_dict
            
            with open(self.dictionary_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Diccionario actualizado en {self.dictionary_path}")
        except Exception as e:
            logger.error(f"Error al guardar el diccionario: {e}")

    def normalize(self, text: str) -> Tuple[str, List[ModismoDetectado]]:
        """
        Detecta modismos en el texto, los reemplaza por su versión normalizada
        y devuelve una lista de los modismos encontrados con sus posiciones originales.
        """
        if not text:
            return "", []

        modismos_encontrados: List[ModismoDetectado] = []
        
        # Ordenar modismos por longitud de la expresión (descendente) 
        sorted_modismos = sorted(self.modismos_dict, key=lambda x: len(x["expresion_original"]), reverse=True)

        matches_info = []
        for modismo in sorted_modismos:
            pattern = r'\b' + re.escape(modismo["expresion_original"]) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
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

        matches_info.sort(key=lambda x: x['start'])

        for match in matches_info:
            modismos_encontrados.append(
                ModismoDetectado(
                    expresion_original=match['original'],
                    expresion_normalizada=match['normalizada'],
                    posicion_inicio=match['start'],
                    posicion_fin=match['end'],
                    accion_usuario='ACEPTADA'
                )
            )

        temp_text = text
        for match in reversed(matches_info):
            temp_text = temp_text[:match['start']] + match['normalizada'] + temp_text[match['end']:]

        return temp_text, modismos_encontrados
