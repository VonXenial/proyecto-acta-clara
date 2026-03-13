# 04 - PROTOTIPO 1: MOTOR DE TRANSCRIPCIÓN (STT)

**Documento:** P1 - STT Engine  
**Versión:** 1.0  
**Fecha:** 13 marzo 2026  
**Responsable:** Agente Backend (Gemini 3 Flash)

---

## 📋 OBJETIVOS
1.  Implementar la carga y preprocesamiento de audio (WAV/MP3).
2.  Integrar `faster-whisper` para conversión de habla a texto local.
3.  Asegurar el uso de binarios locales de FFmpeg.
4.  Retornar objetos `Transcription` estructurados.

---

## 🏗️ ARQUITECTURA TÉCNICA

### 1. Controlador de Audio (`src/controllers/audio_controller.py`)
*   **Librería:** `pydub`.
*   **Requisito:** Configurar `AudioSegment.converter` a `./bin/ffmpeg.exe`.
*   **Funciones:**
    *   Cargar archivos.
    *   Normalizar volumen.
    *   Convertir a formato compatible con Whisper (16kHz, mono).

### 2. Motor STT (`src/services/stt_engine.py`)
*   **Librería:** `faster-whisper`.
*   **Modelo Sugerido:** `small` con `compute_type="int8"`.
*   **Funciones:**
    *   Cargar modelo en CPU (o GPU si está disponible).
    *   Generar segmentos con timestamps.
    *   Calcular probabilidad de idioma.

---

## 🛠️ TAREA PARA EL AGENTE BACKEND
> 1.  Crea `src/controllers/audio_controller.py` con una clase `AudioController` que maneje la carga y preprocesamiento.
> 2.  Crea `src/services/stt_engine.py` con una clase `STTEngine` que encapsule `faster-whisper`.
> 3.  Implementa un script de prueba en `tests/test_p1_stt.py` que transcriba un audio corto.
> 4.  Usa los modelos definidos en `src/models/transcription.py`.

---

## ✅ CRITERIOS DE ACEPTACIÓN
*   [ ] Puede cargar un MP3/WAV sin errores de FFmpeg.
*   [ ] La transcripción devuelve texto coherente.
*   [ ] Se incluyen marcas de tiempo (inicio/fin) por segmento.
*   [ ] El uso de RAM no excede los 3GB durante el proceso.
