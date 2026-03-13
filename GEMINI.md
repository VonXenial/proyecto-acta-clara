# 📜 DIRECTIVAS DEL PROYECTO ACTACLARA

Este archivo es la fuente de verdad para cualquier Agente de IA que trabaje en este repositorio.

## 🎯 RESUMEN DEL PROYECTO
- **Nombre:** ActaClara
- **Meta:** Sistema local de transcripción y normalización de modismos chilenos.
- **Metodología:** Incremental y Prototipos (basado en Tesis 2025).
- **Estado Actual:** v0.4 (P3 - Interfaz Integrada).

## 🎭 MAPEO DE AGENTES (Google Antigravity)
1. **Orquestador:** Claude Opus 4.6 (Thinkings) - Gestión de contexto y .md.
2. **Arquitecto:** Gemini 3.1 pro (High) - Diseño estructural y SQL.
3. **Backend:** Gemini 3 Flash - Lógica STT, NLP y Audio.
4. **UI Specialist:** Claude Sonnet 4.6 (Thinkings) - Tkinter y UX.
5. **Debugger:** GPT-OSS 120B (medium) - Errores y Bitácora de Troubleshooting.

## 📂 ARCHIVOS CRÍTICOS DE CONTEXTO
- `chat_session.history`: Progreso detallado y tareas pendientes.
- `docs/HITOS_Y_CRONOGRAMAS.md`: Timeline y estado de prototipos.
- `docs/09_TROUBLESHOOTING_v1.0.md`: Registro de errores superados.
- `docs/ROLES.md`: Definición profunda de responsabilidades.

## 🛠️ REGLAS DE ORO
1. **Documentación Primero:** Antes de cada hito, actualizar el .md correspondiente en `docs/`.
2. **Registro de Errores:** Cualquier error técnico debe ir a la bitácora de Troubleshooting.
3. **Entorno:** Usar siempre el `venv` y el FFmpeg local en `bin/`.
4. **Respeto al Diseño:** La UI debe seguir los mockups .png en `docs/`.
