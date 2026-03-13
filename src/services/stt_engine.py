import os
import logging
from faster_whisper import WhisperModel
from src.models.transcription import Transcription, TranscripcionSegmento

# Configurar el logger
logger = logging.getLogger("STTEngine")

class STTEngine:
    """
    Servicio de transcripción Speech-to-Text usando faster-whisper.
    """
    
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        """
        Inicializa el modelo de Whisper.
        """
        try:
            logger.info(f"Cargando modelo Whisper '{model_size}' en {device} ({compute_type})...")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Modelo cargado correctamente.")
        except Exception as e:
            logger.error(f"Error al cargar el modelo Whisper: {e}")
            raise

    def transcribe(self, audio_path: str) -> Transcription:
        """
        Transcribe el archivo de audio y devuelve un objeto Transcription.
        """
        try:
            logger.info(f"Iniciando transcripción de: {audio_path}")
            
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=5,
                vad_filter=True,  # Filtro de actividad de voz para ignorar silencios largos
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            transcription_segments = []
            full_text = []
            
            for segment in segments:
                # Mapear a nuestro modelo de dominio
                transcription_segments.append(
                    TranscripcionSegmento(
                        texto=segment.text.strip(),
                        inicio=segment.start,
                        fin=segment.end
                    )
                )
                full_text.append(segment.text.strip())
            
            logger.info(f"Transcripción completada. Idioma detectado: {info.language} ({info.language_probability:.2f})")
            
            return Transcription(
                texto_completo=" ".join(full_text),
                segmentos=transcription_segments,
                idioma_detectado=info.language,
                duracion_procesada=info.duration
            )
            
        except Exception as e:
            logger.error(f"Error durante la transcripción: {e}")
            raise
