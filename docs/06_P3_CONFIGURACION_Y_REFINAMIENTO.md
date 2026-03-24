# 06 - REFINAMIENTO: CONFIGURACIÓN, TEMAS Y MULTIFORMATO

**Estado:** 🏗️ EN DESARROLLO  
**Versión:** 0.6  
**Fecha:** 14 marzo 2026  
**Responsables:** Todos los Agentes

---

## 📋 REQUERIMIENTOS DE CIERRE

### 1. Gestión de Preferencias (`settings.json`)
El sistema debe permitir persistir:
- `appearance`: ["light", "dark"]
- `export_path`: Ruta por defecto para guardar archivos.
- `language`: ["es", "en"]
- `stt_model`: Tamaño del modelo Whisper.

### 2. Exportación a PDF
- Implementar clase `PdfExporter` siguiendo la interfaz `ExporterInterface`.
- El PDF debe mantener la misma estructura jerárquica que el DOCX.

### 3. Personalización de Interfaz (UI)
- **Modo Oscuro:** Fondo `#212529`, Texto `#F8F9FA`, Botones con azul contrastado.
- **Multi-idioma:** Soporte inicial para Español e Inglés en menús y diálogos.
- **Historial Dinámico:** Cargar las últimas 10 actas reales desde SQLite en el panel lateral.

---

## 🏗️ TAREAS DE LOS AGENTES

### A2: ARQUITECTO
- Diseñar la estructura de `src/utils/config_manager.py`.
- Definir el diccionario de traducción para i18n.

### A3: BACKEND
- Implementar `ConfigManager`.
- Implementar `PdfExporter` usando la librería `fpdf2`.
- Añadir método `get_all_actas()` al `DBManager`.

### A4: UI SPECIALIST
- Implementar lógica de cambio de tema (re-render de widgets).
- Crear la vista de Configuración funcional.
- Poblar el historial lateral con datos reales.

---
*Este documento marca el inicio de la recta final hacia el MVP v1.0.*
