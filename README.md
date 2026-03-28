# ActaClara 🎙️✨ (v1.4 - Professional Edition)

**ActaClara** es un sistema inteligente de transcripción multilingüe y normalización de modismos diseñado para optimizar la generación de actas en entornos empresariales.

El proyecto nace para transformar el habla coloquial (especialmente el robusto modismo chileno) en texto formal y estructurado mediante IA local, garantizando la privacidad y la precisión técnica.

---

## 🚀 Características Principales (Estado Actual)

- **Especialista en Modismos Chilenos:** Diccionario maestro integrado con más de 500 términos normalizados. El motor Whisper ha sido optimizado mediante *Prompt Engineering* para entender jergas complejas sin alucinaciones.
- **Gestión Profesional de Archivos:** Estructura de carpetas intuitiva:
  - `Actas/`: Destino oficial de exportaciones de usuario.
  - `backups/`: Respaldos automáticos internos del sistema.
  - `data/recordings/`: Galería oficial de grabaciones originales de la sesión.
- **Identidad Visual:** Integración de icono personalizado en la barra de tareas de Windows y UI pulida basada en Figma.
- **Transcripción STT Local:** Utiliza el motor `Faster-Whisper` (Small/Medium) para un reconocimiento de voz rápido y preciso totalmente offline.
- **Arquitectura Robusta:** Patrón **MVC**, persistencia en **SQLite** y procesamiento asíncrono multihilo.

---

## 🏗️ Arquitectura del Sistema

El software ha alcanzado su **Fase Pro (v1.4)** tras completar los siguientes hitos:

1.  **v0.1 - v1.0:** Cimientos de STT y base de datos.
2.  **v1.2 (P2+):** Refinamiento de la inteligencia de normalización lingüística.
3.  **v1.4 (Fase Actual):** Optimización de UX, limpieza profunda de entorno y preparación para despliegue (EXE/AppImage).

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.10 - 3.14
- **IA/ML:** Faster-Whisper, PyTorch (Optimizado para CPU/GPU)
- **Audio:** FFmpeg (Binarios incluidos), Pydub, SoundDevice
- **Base de Datos:** SQLite
- **UI:** Tkinter Modernizado
- **Documentación:** Markdown, python-docx, fpdf2

---

## 📦 Instalación y Desarrollo

### Prerrequisitos
- Python 3.10 o superior.
- FFmpeg (binarios incluidos localmente en `bin/`).

### Pasos
1.  **Clonar:** `git clone https://github.com/VonXenial/proyecto-acta-clara.git`
2.  **Entorno:** `python -m venv venv` y activa con `.\venv\Scripts\activate`.
3.  **Dependencias:** `pip install -r requirements.txt`
4.  **Lanzar:** `python src/main.py`

---

## 🎓 Proyecto Académico
Desarrollado bajo los lineamientos del Instituto Profesional Santo Tomás (2025-2026).

---
**Autor:** Ian Leonardo Castro Contreras  
**Estado Actual:** Estable - Listo para empaquetado y despliegue masivo.
