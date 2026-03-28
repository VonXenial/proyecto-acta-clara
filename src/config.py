import os

# Configuración Global ActaClara
VERSION = "0.4"

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
BIN_DIR = os.path.join(BASE_DIR, "bin")

# Configuración Base de Datos
DB_PATH = os.path.join(DATA_DIR, "actaclara.db")

# Configuración STT
FFMPEG_PATH = os.path.join(BIN_DIR, "ffmpeg.exe")
WHISPER_MODEL = "small"
COMPUTE_TYPE = "int8"

# Configuración Diccionario
DICTIONARY_PATH = os.path.join(DATA_DIR, "diccionarios", "modismos_es_CL_v1.0.json")

# Carpetas de datos generados
RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
