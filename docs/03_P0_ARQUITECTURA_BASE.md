# 03 - PROTOTIPO 0: ARQUITECTURA BASE Y PERSISTENCIA

**Estado:** ✅ COMPLETADO  
**Fecha:** 13 marzo 2026  
**Responsables:** Arquitecto (Gemini High) & Backend (Gemini Flash)

---

## 📋 RESUMEN TÉCNICO
Se ha establecido la base estructural del sistema siguiendo el patrón **MVC (Modelo-Vista-Controlador)**. Este prototipo garantiza que los datos de las actas y los modismos detectados puedan guardarse y recuperarse localmente sin depender de la nube.

## 🗄️ MODELO DE DATOS (Persistencia)
Se utiliza **SQLite** por su portabilidad. El esquema se encuentra en `src/database/schema.sql`.

### Tablas Principales:
*   **actas:** Almacena metadatos de la reunión (título, audio, ruta docx, WER).
*   **modismos_detectados:** Relación 1:N con actas. Guarda la expresión original, la formalizada y la posición en el texto.

## 📂 ESTRUCTURA DE CLASES (`src/models/`)
Se implementaron clases de datos (Dataclasses) para asegurar la integridad del código:
*   `Acta`: Entidad principal.
*   `ModismoDetectado`: Detalle de cada hallazgo.
*   `Transcription`: Estructura para el motor STT.

## ⚙️ COMPONENTE: DBManager
Ubicado en `src/database/db_manager.py`, este componente maneja:
1.  **Singleton Pattern:** Una única conexión a la base de datos.
2.  **Inicialización Automática:** Crea las tablas si no existen.
3.  **CRUD Recursivo:** Al guardar un Acta, guarda automáticamente todos sus modismos.

## ✅ PRUEBAS DE VALIDACIÓN
*   **Test:** `tests/test_db.py`
*   **Resultado:** 100% éxito en inserción y recuperación de objetos complejos.
*   **Logs:** Verificables en `logs/database.log`.

---
*Este documento es parte de la entrega técnica de ActaClara.*
