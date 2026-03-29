import os
import sys

# Configuración Global ActaClara
VERSION = "1.4"

# 1. Rutas de Aplicación (Recursos de solo lectura: assets, diccionarios, bin)
if getattr(sys, 'frozen', False):
    # Si estamos corriendo como un ejecutable compilado por PyInstaller
    APP_DIR = sys._MEIPASS
else:
    # Si estamos corriendo desde el código fuente
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = os.path.join(APP_DIR, "bin")

# 2. Rutas de Usuario (Lectura/Escritura: base de datos, grabaciones, exportaciones)
# Identificar la carpeta Documentos de forma segura en Windows
if os.name == "nt":
    try:
        import winreg
        path = winreg.QueryValueEx(
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"),
            "Personal"
        )[0]
        USER_DOCS = path
    except Exception:
        USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents")
else:
    USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents")

if not os.path.exists(USER_DOCS):
    USER_DOCS = os.path.expanduser("~") # Fallback al directorio Home

USER_DATA_DIR = os.path.join(USER_DOCS, "ActaClara")

# Crear carpetas de usuario si no existen
os.makedirs(USER_DATA_DIR, exist_ok=True)
DATA_DIR = os.path.join(USER_DATA_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Configuración Base de Datos
DB_PATH = os.path.join(DATA_DIR, "actaclara.db")

# Configuración STT
FFMPEG_PATH = os.path.join(BIN_DIR, "ffmpeg.exe")
WHISPER_MODEL = "small"
COMPUTE_TYPE = "int8"

# Configuración Diccionario (Recurso de Solo Lectura)
DICTIONARY_PATH = os.path.join(APP_DIR, "data", "diccionarios", "modismos_es_CL_v1.0.json")

# Carpetas de datos generados (Usuario)
RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)
