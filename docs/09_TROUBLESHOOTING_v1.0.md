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
| **ERR_003** | 13/03 | FFmpeg no encontrado en el sistema | CRÍTICO | ✅ SOLUCIONADO |
| **ERR_004** | 13/03 | Error de importación en `pydub` (falso negativo) | MENOR | ✅ SOLUCIONADO |
| **ERR_005** | 13/03 | Truncamiento de contexto por exceso de datos (PDF OCR) | CRÍTICO | ⚠️ MITIGADO |

---

## 🔍 DETALLE DE INCIDENCIAS Y SOLUCIONES

### 🔴 ERR_001: Python no detectado en PATH (Windows)
*   **Síntoma:** El comando `python --version` retornaba error o redirigía a la Microsoft Store.
*   **Solución:** Instalación manual de Python 3.14.3 y configuración manual de la variable de entorno `Path`.

### 🔴 ERR_002: Incompatibilidad de Librerías ML con Python 3.14
*   **Síntoma:** `pip install torch==2.1.0` fallaba.
*   **Solución:** Se editó `requirements.txt` para eliminar las versiones fijas, permitiendo versiones más recientes compatibles con Python 3.14.

### 🟠 ERR_003: FFmpeg no encontrado
*   **Síntoma:** El script `verify_setup.py` indica que FFmpeg no está instalado.
*   **Solución:** Descarga manual de binarios esenciales a la carpeta `bin/` y configuración de ruta absoluta en `AudioController`.

### 🟡 ERR_004: Falso Negativo en Importación de `pydub`
*   **Síntoma:** `verify_setup.py` reportaba `pydub` como NO instalado.
*   **Solución:** Validación manual dentro del `venv`.

### 🔴 ERR_005: Truncamiento de Contexto por Exceso de Datos
*   **Síntoma:** `agent executor error: could not convert a single message before hitting truncation`.
*   **Causa:** Saturación del historial debido al OCR masivo del PDF de tesis.
*   **Solución:** Uso de resúmenes estratégicos y evitar la re-lectura de archivos de más de 500 líneas.
*   **Prevención:** Los agentes deben ser quirúrgicos en sus lecturas.

---

## 💡 LECCIONES APRENDIDAS (PARA AGENTES IA)

1.  **Flexibilidad de Versiones:** Dejar que el resolver de dependencias actúe en versiones de Python muy nuevas.
2.  **Validez de Contexto:** No sature el historial con datos crudos masivos; use los archivos `.md` como puntos de control.

---
*Este documento es actualizado por el Orquestador y revisado por el Agente Debugger.*
