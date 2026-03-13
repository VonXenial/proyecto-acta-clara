# 09 - BITÁCORA DE ERRORES Y SOLUCIONES (TROUBLESHOOTING)

**Proyecto:** ActaClara  
**Versión:** 1.0  
**Última Actualización:** 13 marzo 2026  
**Estado:** Activo - Fase de Setup

---

## 📋 RESUMEN DE INCIDENCIAS

| ID | Fecha | Problema | Impacto | Estado |
|:---|:---:|:---|:---|:---|
| **ERR_001** | 12/03 | Python no detectado en PATH (Windows) | BLOQUEANTE | ✅ SOLUCIONADO |
| **ERR_002** | 13/03 | Incompatibilidad Python 3.14 con Torch 2.1.0 | BLOQUEANTE | ✅ SOLUCIONADO |
| **ERR_003** | 13/03 | FFmpeg no encontrado en el sistema | CRÍTICO | 🔧 EN PROCESO |
| **ERR_004** | 13/03 | Error de importación en `pydub` (falso negativo) | MENOR | ✅ SOLUCIONADO |

---

## 🔍 DETALLE DE INCIDENCIAS Y SOLUCIONES

### 🔴 ERR_001: Python no detectado en PATH (Windows)
*   **Síntoma:** El comando `python --version` retornaba error o redirigía a la Microsoft Store.
*   **Causa:** Las variables de entorno de Windows priorizaban los "App Execution Aliases" de Microsoft sobre la instalación real de Python.
*   **Solución:**
    1.  Instalación manual de Python 3.14.3 desde el instalador oficial.
    2.  Configuración manual de la variable de entorno `Path` para incluir `...\Programs\Python\Python314\`.
    3.  Reinicio de la terminal del IDE.

### 🔴 ERR_002: Incompatibilidad de Librerías ML con Python 3.14
*   **Síntoma:** `pip install torch==2.1.0` fallaba con `Could not find a version...`.
*   **Causa:** Python 3.14 es una versión extremadamente reciente. `torch` y `faster-whisper` no tienen binarios pre-compilados para las versiones específicas solicitadas en el `requirements.txt` original.
*   **Solución:**
    1.  Se editó `requirements.txt` para eliminar las versiones fijas (`==`).
    2.  Se permitió que `pip` buscara la versión más reciente compatible (`torch 2.10.0` y `faster-whisper 1.2.1`).
    3.  **Resultado:** Instalación exitosa en entorno virtual (`venv`).

### 🟠 ERR_003: FFmpeg no encontrado
*   **Síntoma:** El script `verify_setup.py` indica que FFmpeg no está instalado.
*   **Causa:** FFmpeg es una herramienta externa a Python y no se instala vía `pip`.
*   **Estado:** Se requiere instalación binaria manual o automatizada para permitir el procesamiento de audio en `pydub`.

### 🟡 ERR_004: Falso Negativo en Importación de `pydub`
*   **Síntoma:** `verify_setup.py` reportaba `pydub` como NO instalado a pesar de éxito en `pip install`.
*   **Causa:** El script de verificación intentaba importar `pydub` de forma incorrecta o el entorno virtual no estaba totalmente refrescado.
*   **Solución:** Activación explícita del script dentro del `venv` y validación manual de la ruta de paquetes.

---

## 💡 LECCIONES APRENDIDAS (PARA AGENTES IA)

1.  **Flexibilidad de Versiones:** En entornos con versiones de Python muy nuevas, no forzar versiones de librerías de ML; dejar que el resolver de dependencias haga su trabajo.
2.  **Validación de PATH:** Siempre verificar `where python` antes de proceder con instalaciones complejas.
3.  **Roles de Documentación:** Cada error debe ser registrado inmediatamente para evitar la repetición de diagnósticos fallidos por parte de otros agentes.

---
*Este documento es actualizado por el Orquestador y revisado por el Agente Debugger.*
