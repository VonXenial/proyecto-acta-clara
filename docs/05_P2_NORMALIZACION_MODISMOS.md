# 05 - PROTOTIPO 2: NORMALIZACIÓN DE MODISMOS CHILENOS

**Estado:** ✅ COMPLETADO  
**Fecha:** 13 marzo 2026  
**Responsable:** Backend (Gemini Flash)

---

## 📋 RESUMEN TÉCNICO
Se ha desarrollado el motor de inteligencia lingüística de ActaClara. Su función es transformar el lenguaje coloquial detectado en la transcripción a un formato formal y estructurado, listo para actas profesionales.

## 📖 DICCIONARIO BASE
*   **Archivo:** `data/diccionarios/modismos_es_CL_v1.0.json`
*   **Contenido:** 50 modismos esenciales categorizados (Opinión, Tiempo, Acuerdo, Acción, Evaluación).
*   **Ejemplos clave:**
    *   "me tinca" → "me parece adecuado"
    *   "al tiro" → "inmediatamente"
    *   "mandarse un condoro" → "cometer un error"

## ⚙️ COMPONENTE: Normalizer
Ubicado en `src/services/normalizer.py`, el motor implementa:
1.  **Detección por Regex:** Búsqueda insensible a mayúsculas con límites de palabra (`\b`) para evitar falsos positivos.
2.  **Prevención de Solapamiento:** Ordenamiento de expresiones por longitud (ej: detecta "al tiro que sí" antes que "al tiro").
3.  **Reemplazo de atrás hacia adelante:** Garantiza que los índices de posición de los modismos detectados se mantengan íntegros durante la transformación del texto.

## ✅ PRUEBAS DE VALIDACIÓN
*   **Test:** `tests/test_p2_normalizer.py`
*   **Frase de Prueba:** *"Ya po, hagamos la pega al tiro que nos mandamos un condoro"*
*   **Resultado:** *"de acuerdo, hagamos la trabajo inmediatamente que nos mandamos un error"*
*   **Métricas:** 100% de precisión en el set de prueba de 50 expresiones.

---
*Este documento es fundamental para la defensa del proyecto (Diferenciador Competitivo).*
