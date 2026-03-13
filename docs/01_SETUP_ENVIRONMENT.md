# 01 - CONFIGURACIÓN DEL ENTORNO DE DESARROLLO

**Documento:** Setup Environment  
**Versión:** 1.0  
**Fecha:** 12 marzo 2026  
**Tiempo estimado:** 2-3 horas  
**Prerequisitos:** Python 3.10+ instalado

---

## 📋 ÍNDICE

1. [Verificación de Python](#verificación-de-python)
2. [Creación de Entorno Virtual](#entorno-virtual)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Instalación de FFmpeg](#instalación-de-ffmpeg)
5. [Configuración de Gemini CLI](#configuración-gemini-cli)
6. [Estructura de Carpetas](#estructura-de-carpetas)
7. [Verificación del Setup](#verificación-del-setup)
8. [Troubleshooting](#troubleshooting)

---

## 1️⃣ VERIFICACIÓN DE PYTHON

### Windows (CMD o PowerShell):
```cmd
python --version
# Debe mostrar: Python 3.10.x o superior
```

### Si no tienes Python 3.10+:
1. Descargar desde: https://www.python.org/downloads/
2. Durante instalación: ✅ Marcar "Add Python to PATH"
3. Reiniciar terminal

---

## 2️⃣ CREACIÓN DE ENTORNO VIRTUAL

### ¿Por qué un entorno virtual?
```
✅ Aísla dependencias del proyecto
✅ Evita conflictos con otros proyectos
✅ Facilita reproducibilidad
```

### Comandos (Windows CMD):
```cmd
# Navegar a donde quieras crear el proyecto
cd C:\Users\TuUsuario\Documents\

# Crear carpeta del proyecto
mkdir ActaClara
cd ActaClara

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Deberías ver (venv) al inicio de la línea de comandos
(venv) C:\Users\TuUsuario\Documents\ActaClara>
```

### Comandos (Git Bash en Windows):
```bash
cd /c/Users/TuUsuario/Documents/
mkdir ActaClara
cd ActaClara

python -m venv venv
source venv/Scripts/activate

# Deberías ver (venv) al inicio
(venv) user@PC MINGW64 ~/Documents/ActaClara $
```

### Comandos (Warp Terminal):
```bash
# Igual que Git Bash
cd ~/Documents/
mkdir ActaClara
cd ActaClara

python -m venv venv
source venv/Scripts/activate
```

---

## 3️⃣ INSTALACIÓN DE DEPENDENCIAS

### Crear archivo requirements.txt

```cmd
# Asegúrate de estar en ActaClara/ con (venv) activo
# Crear archivo requirements.txt
```

**Contenido de `requirements.txt`:**
```txt
# ==========================================
# ACTACLARA - DEPENDENCIAS
# Versión: 1.0
# Python: 3.10+
# Fecha: 12 marzo 2026
# ==========================================

# Motor de Transcripción
faster-whisper==1.0.0
torch==2.1.0
torchaudio==2.1.0

# Procesamiento de Audio
pydub==0.25.1

# Exportación de Documentos
python-docx==1.1.0

# Utilidades
python-dotenv==1.0.0

# Testing (opcional para MVP)
pytest==7.4.0
```

### Instalar todas las dependencias:

```cmd
# Con entorno virtual activado (venv)
pip install --upgrade pip
pip install -r requirements.txt

# Esto tomará 5-15 minutos dependiendo de tu conexión
```

### Verificar instalación:
```cmd
pip list

# Deberías ver algo como:
# faster-whisper     1.0.0
# torch              2.1.0
# python-docx        1.1.0
# pydub              0.25.1
# ...
```

---

## 4️⃣ INSTALACIÓN DE FFMPEG

### ¿Por qué FFmpeg?
```
FFmpeg es necesario para que pydub procese audio
(conversión WAV/MP3, normalización, recorte)
```

### Opción A: Windows - Instalación Manual (Recomendado)

**Paso 1: Descargar**
```
1. Ir a: https://www.gyan.dev/ffmpeg/builds/
2. Descargar: ffmpeg-release-essentials.zip
3. Descomprimir en C:\ffmpeg\
```

**Paso 2: Agregar al PATH**
```
1. Windows Search → "variables de entorno"
2. Variables de entorno → Path → Editar
3. Nuevo → Agregar: C:\ffmpeg\bin
4. Aceptar todo
5. Reiniciar CMD/PowerShell/GitBash
```

**Paso 3: Verificar**
```cmd
ffmpeg -version

# Debe mostrar info de FFmpeg, no error
```

### Opción B: Windows - Con Chocolatey
```cmd
# Si tienes Chocolatey instalado:
choco install ffmpeg

# Verificar
ffmpeg -version
```

### Opción C: Windows - Con Scoop
```cmd
# Si usas Scoop:
scoop install ffmpeg

# Verificar
ffmpeg -version
```

---

## 5️⃣ CONFIGURACIÓN DE GEMINI CLI

### Instalar Gemini CLI

```cmd
# Con (venv) activo
pip install google-generativeai

# O si prefieres la CLI oficial de Google:
pip install google-ai-generativelanguage
```

### Obtener API Key

1. Ir a: https://aistudio.google.com/app/apikey
2. Crear nuevo API key
3. Copiar la key

### Configurar Variables de Entorno

**Crear archivo `.env` en la raíz del proyecto:**

```bash
# ActaClara/.env
GEMINI_API_KEY=tu_api_key_aqui
GOOGLE_AI_MODEL=gemini-1.5-pro
```

**Crear `.env.example` (para compartir sin exponer keys):**
```bash
# ActaClara/.env.example
GEMINI_API_KEY=your_api_key_here
GOOGLE_AI_MODEL=gemini-1.5-pro
```

### Verificar Gemini CLI

**Crear script de prueba `test_gemini.py`:**

```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

response = model.generate_content("Di 'Hola, ActaClara está listo'")
print(response.text)
```

**Ejecutar:**
```cmd
python test_gemini.py

# Debe mostrar: Hola, ActaClara está listo
```

---

## 6️⃣ ESTRUCTURA DE CARPETAS

### Crear estructura completa:

```cmd
# Desde ActaClara/ con (venv) activo

# Crear todas las carpetas de una vez
mkdir docs docs\versions
mkdir src src\controllers src\models src\services src\ui src\utils src\database
mkdir data data\diccionarios data\audios_prueba data\actas_exportadas
mkdir tests
mkdir logs
```

### Verificar estructura:
```cmd
tree /F

# Debe mostrar:
ActaClara
├── venv\
├── docs\
│   └── versions\
├── src\
│   ├── controllers\
│   ├── models\
│   ├── services\
│   ├── ui\
│   ├── utils\
│   └── database\
├── data\
│   ├── diccionarios\
│   ├── audios_prueba\
│   └── actas_exportadas\
├── tests\
├── logs\
├── requirements.txt
├── .env
└── .env.example
```

### Crear archivos `__init__.py` en carpetas src:

```cmd
# Windows CMD:
type nul > src\__init__.py
type nul > src\controllers\__init__.py
type nul > src\models\__init__.py
type nul > src\services\__init__.py
type nul > src\ui\__init__.py
type nul > src\utils\__init__.py
type nul > src\database\__init__.py

# Git Bash / Warp:
touch src/__init__.py
touch src/controllers/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/ui/__init__.py
touch src/utils/__init__.py
touch src/database/__init__.py
```

---

## 7️⃣ VERIFICACIÓN DEL SETUP

### Script de Validación Automática

**Crear `verify_setup.py` en la raíz:**

```python
"""
Script de verificación del entorno ActaClara
Versión: 1.0
"""

import sys
import subprocess
import importlib

def check_python_version():
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere 3.10+")
        return False

def check_package(package_name):
    try:
        importlib.import_module(package_name.replace('-', '_'))
        print(f"✅ {package_name} instalado")
        return True
    except ImportError:
        print(f"❌ {package_name} NO instalado")
        return False

def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg instalado")
            return True
    except:
        pass
    print("❌ FFmpeg NO instalado o no en PATH")
    return False

def check_folders():
    import os
    required_folders = [
        'docs', 'src', 'data', 'tests', 'logs',
        'src/controllers', 'src/models', 'src/services',
        'src/ui', 'src/utils', 'src/database'
    ]
    all_ok = True
    for folder in required_folders:
        if os.path.isdir(folder):
            print(f"✅ Carpeta {folder}/")
        else:
            print(f"❌ Carpeta {folder}/ NO existe")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE ENTORNO ACTACLARA")
    print("=" * 60)
    
    results = []
    
    print("\n1. Verificando Python...")
    results.append(check_python_version())
    
    print("\n2. Verificando paquetes...")
    packages = ['faster_whisper', 'torch', 'pydub', 'docx', 'dotenv']
    for pkg in packages:
        results.append(check_package(pkg))
    
    print("\n3. Verificando FFmpeg...")
    results.append(check_ffmpeg())
    
    print("\n4. Verificando estructura de carpetas...")
    results.append(check_folders())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ENTORNO CONFIGURADO CORRECTAMENTE")
        print("🚀 Listo para comenzar con P0")
    else:
        print("⚠️ HAY PROBLEMAS EN LA CONFIGURACIÓN")
        print("Ver errores arriba y corregir")
    print("=" * 60)
```

**Ejecutar verificación:**
```cmd
python verify_setup.py

# Todos los items deben mostrar ✅
```

---

## 8️⃣ TROUBLESHOOTING

### Problema 1: torch no se instala
```
Error: Could not find a version that satisfies torch...

SOLUCIÓN:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Problema 2: faster-whisper da error
```
Error: No module named 'faster_whisper'

SOLUCIÓN:
pip uninstall faster-whisper
pip install faster-whisper --no-cache-dir
```

### Problema 3: FFmpeg no se encuentra
```
Error: FileNotFoundError: [WinError 2] ffmpeg

SOLUCIÓN:
1. Verificar que C:\ffmpeg\bin existe
2. Verificar que está en PATH (echo %PATH%)
3. Reiniciar terminal completamente
4. Como último recurso: reiniciar PC
```

### Problema 4: python-docx no genera DOCX
```
Error: No module named 'lxml'

SOLUCIÓN:
pip install lxml
```

### Problema 5: Gemini API no responde
```
Error: google.api_core.exceptions.PermissionDenied

SOLUCIÓN:
1. Verificar que .env tiene API key correcta
2. Verificar que API key está activa en AI Studio
3. Verificar límites de cuota de API
```

---

## ✅ CHECKLIST DE FINALIZACIÓN

Marca cuando completes:

- [ ] Python 3.10+ verificado
- [ ] Entorno virtual creado y activado
- [ ] Todas las dependencias instaladas (requirements.txt)
- [ ] FFmpeg instalado y en PATH
- [ ] Gemini CLI configurado y probado
- [ ] Estructura de carpetas creada
- [ ] `verify_setup.py` ejecutado con éxito (todo ✅)
- [ ] `.gitignore` creado (opcional pero recomendado)

---

## 📄 CONTENIDO SUGERIDO DE `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Entorno
.env
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/*.log
*.log

# Base de datos
data/*.db
data/*.db-journal

# Archivos temporales
*.tmp
*.temp

# Sistema
.DS_Store
Thumbs.db

# Audios grandes (opcional)
data/audios_prueba/*.wav
data/audios_prueba/*.mp3
```

---

## 🎯 PRÓXIMO PASO

Una vez completado este setup:

**→ Leer `02_DICCIONARIO_MODISMOS.md`**

Este documento te guiará en la creación del diccionario inicial de 50 modismos chilenos, que es CRÍTICO para P2.

---

**Versión:** 1.0  
**Última actualización:** 12 marzo 2026  
**Tiempo invertido estimado:** 2-3 horas  
**Estado:** ✅ Listo para uso
