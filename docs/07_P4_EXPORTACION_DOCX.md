# 07 - PROTOTIPO 4: EXPORTACIÓN Y REPOSITORIO (DOCX)

**Estado:** ⏳ PENDIENTE  
**Versión:** 0.5  
**Fecha:** 14 marzo 2026 (Planificado)  
**Responsables:** Arquitecto (A2) & Backend (A3)

---

## 📋 OBJETIVOS
1.  Generar documentos **DOCX** profesionales a partir de la transcripción normalizada.
2.  Aplicar una **plantilla corporativa** (Encabezado, Título, Secciones).
3.  Estructurar el contenido en secciones:
    *   Información General (Proyecto, Objetivo, Fecha).
    *   Asistentes.
    *   Desarrollo de la Reunión (Texto normalizado).
    *   Acuerdos y Compromisos.
4.  Persistir la ruta del archivo generado en la base de datos SQLite.

## 🏗️ ESPECIFICACIONES TÉCNICAS
- **Librería:** `python-docx` (ya instalada).
- **Componente:** `src/services/exporter.py` (`DocxExporter`).
- **Formato de Salida:** `data/actas_exportadas/{titulo}_{fecha}.docx`.
- **Relación DB:** Actualizar la columna `archivo_docx_ruta` en la tabla `actas`.

## ✅ CRITERIOS DE ACEPTACIÓN
- [ ] El archivo generado se abre correctamente en Microsoft Word / LibreOffice.
- [ ] Los modismos normalizados aparecen correctamente en el documento final.
- [ ] Se incluyen los metadatos (Participantes, Objetivo) capturados en la UI.
- [ ] La ruta del archivo queda registrada en SQLite vinculada al Acta ID correspondiente.

---
*Este documento guía el desarrollo del prototipo final antes de la fase de refinamiento.*
