"""
Script de verificación del entorno ActaClara
Versión: 1.0
"""

import sys
import subprocess
import importlib
import os

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
