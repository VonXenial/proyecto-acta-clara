# ActaClara 🎙️✨

**ActaClara** es un sistema inteligente de transcripción multilingüe y normalización de modismos diseñado para optimizar la generación de actas en entornos empresariales.

El proyecto nace para resolver la pérdida de productividad y las ambigüedades lingüísticas en reuniones multiculturales, transformando el habla coloquial (especialmente el modismo chileno) en texto formal y estructurado mediante IA local.

---

## 🚀 Características Principales

- **Transcripción STT Local:** Utiliza el motor `Faster-Whisper` para un reconocimiento de voz rápido y preciso sin depender de la nube.
- **Normalización de Modismos:** Motor NLP basado en reglas y diccionarios JSON que detecta y formaliza expresiones coloquiales (ej: *"me tinca"* → *"me parece adecuado"*).
- **Interfaz Moderna:** GUI desarrollada en Python con `Tkinter/ttk`, siguiendo un diseño minimalista y funcional.
- **Arquitectura Robusta:** Implementado bajo el patrón **MVC** (Modelo-Vista-Controlador) con persistencia en **SQLite**.
- **Procesamiento Multihilo:** Garantiza una experiencia de usuario fluida al ejecutar la IA en hilos separados de la interfaz gráfica.

---

## 🏗️ Arquitectura del Sistema

El software se desarrolla siguiendo una **metodología incremental y basada en prototipos**:

1.  **v0.1 (P0):** Persistencia de datos y modelos de dominio.
2.  **v0.2 (P1):** Motor de transcripción Speech-to-Text.
3.  **v0.3 (P2):** Inteligencia de normalización lingüística.
4.  **v0.4 (P3):** Interfaz de usuario integrada y responsiva.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.10 - 3.14
- **IA/ML:** Faster-Whisper, PyTorch
- **Audio:** FFmpeg, Pydub
- **Base de Datos:** SQLite
- **UI:** Tkinter (Standard Library)
- **Documentación:** Markdown, python-docx

---

## 📦 Instalación y Configuración

### Prerrequisitos
- Python 3.10 o superior.
- FFmpeg (binarios incluidos localmente en `bin/` para portabilidad en Windows).

### Pasos
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/VonXenial/proyecto-acta-clara.git
    cd proyecto-acta-clara
    ```
2.  **Crear y activar entorno virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Ejecutar verificación:**
    ```bash
    python verify_setup.py
    ```
5.  **Lanzar aplicación:**
    ```bash
    python src/ui/main_window.py
    ```

---

## 👥 Agentes de Desarrollo (Estrategia Multi-IA)

Este proyecto es orquestado mediante una estructura de agentes especializados:
- **Orquestador:** Gestión de contexto y flujos.
- **Arquitecto:** Diseño estructural y SQL.
- **Backend:** Lógica de negocio y motores de IA.
- **UI Specialist:** Diseño y experiencia de usuario.
- **Debugger:** Calidad y resolución de incidencias.

---

## 📄 Licencia

Este proyecto se desarrolla bajo los lineamientos académicos del Instituto Profesional Santo Tomás (2025-2026).

---
**Autor:** Ian Leonardo Castro Contreras  
**Contacto:** pourplesoul01@gmail.com
