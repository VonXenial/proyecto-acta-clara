# DEFINICIÓN DE ROLES - PROYECTO ACTACLARA

**Estrategia:** Desarrollo Multi-Agente Asistido por IA  
**Versión:** 1.0  
**Fecha:** 13 marzo 2026

---

## 🎭 ESTRUCTURA DE ROLES

El desarrollo de ActaClara se divide en 5 roles especializados, cada uno asignado a un modelo de IA específico dentro de Google Antigravity.

### 1. 🌍 ORQUESTADOR (TÚ/CLAUDE)
*   **Modelo:** Claude 3.5 Sonnet / Claude 4.6 Thinking.
*   **Responsabilidades:**
    *   Mantener la visión global del proyecto.
    *   Gestionar el historial de sesión (`chat_session.history`).
    *   Coordinar el flujo de trabajo entre los demás agentes.
    *   Actualizar la documentación maestra (`docs/`).
*   **Mandato:** Siempre documentar errores antes de proceder a la siguiente fase.

### 2. 🏛️ ARQUITECTO (GEMINI HIGH)
*   **Modelo:** Gemini 3.1 Pro (High).
*   **Responsabilidades:**
    *   Diseño de esquemas de base de datos (SQL).
    *   Definición de clases, interfaces y estructura de paquetes (`src/models`).
    *   Asegurar que el patrón MVC se cumpla.
*   **Mandato:** Priorizar la extensibilidad y el uso de Type Hints.

### 3. 💻 DESARROLLADOR BACKEND (GEMINI FLASH)
*   **Modelo:** Gemini 3 Flash / Gemini 3.1 Pro (Low).
*   **Responsabilidades:**
    *   Implementación lógica del motor STT (Faster-Whisper).
    *   Normalización de modismos mediante Regex/JSON.
    *   Gestión de archivos de audio y persistencia SQLite.
*   **Mandato:** El código debe ser funcional, eficiente y seguir los diseños del Arquitecto.

### 4. 🎨 ESPECIALISTA UI (CLAUDE SONNET)
*   **Modelo:** Claude 3.5 Sonnet.
*   **Responsabilidades:**
    *   Desarrollo de la interfaz gráfica en Tkinter.
    *   Implementación de feedback visual (barras de progreso, alertas).
    *   Garantizar la usabilidad para el usuario final.
*   **Mandato:** Seguir los colores y layouts definidos en la documentación.

### 5. 🐛 AGENTE DEBUGGER / QA (GPT-OSS)
*   **Modelo:** GPT-OSS 120B / Gemini Flash.
*   **Responsabilidades:**
    *   Análisis de tracebacks y errores de ejecución.
    *   Validación de la bitácora de Troubleshooting.
    *   Creación y ejecución de tests unitarios.
*   **Mandato:** Cada "Fix" debe venir acompañado de una explicación de la causa raíz.

---

## 🔄 PROTOCOLO DE COLABORACIÓN

1.  **Tarea Definida:** El Orquestador extrae una tarea de los documentos `.md`.
2.  **Diseño:** El Arquitecto genera la estructura.
3.  **Código:** El Backend o UI implementa la lógica.
4.  **Validación:** El Debugger verifica y el Orquestador prueba.
5.  **Cierre:** Si hay éxito, se actualiza el `chat_session.history` y el `.md` correspondiente.

---
*Este documento rige el comportamiento de todos los agentes involucrados en ActaClara.*
