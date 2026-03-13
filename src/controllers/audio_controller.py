import os
import logging
from pydub import AudioSegment

# Configurar el logger
logger = logging.getLogger("AudioController")

class AudioController:
    """
    Controlador para el preprocesamiento de audio usando pydub y ffmpeg.
    """
    
    def __init__(self, ffmpeg_path: str = "bin/ffmpeg.exe"):
        """
        Inicializa el controlador y configura la ruta de FFmpeg.
        """
        # Convertir a ruta absoluta para evitar problemas con directorios relativos
        abs_ffmpeg_path = os.path.abspath(ffmpeg_path)
        
        if os.path.exists(abs_ffmpeg_path):
            AudioSegment.converter = abs_ffmpeg_path
            logger.info(f"FFmpeg configurado en: {abs_ffmpeg_path}")
        else:
            logger.warning(f"No se encontró FFmpeg en {abs_ffmpeg_path}. Se usará la configuración global del sistema.")

    def load_audio(self, file_path: str) -> AudioSegment:
        """
        Carga un archivo de audio (WAV, MP3, etc.).
        """
        try:
            audio = AudioSegment.from_file(file_path)
            logger.info(f"Audio cargado exitosamente: {file_path}")
            return audio
        except Exception as e:
            logger.error(f"Error al cargar audio {file_path}: {e}")
            raise

    def preprocess_for_whisper(self, audio: AudioSegment, output_path: str) -> str:
        """
        Normaliza y convierte el audio al formato óptimo para Whisper:
        16kHz, mono, formato WAV.
        """
        try:
            # 1. Normalizar volumen (opcional pero recomendado)
            # normalized_audio = audio.normalize() # Podría ser demasiado lento para audios largos
            
            # 2. Convertir a 16kHz y Mono
            processed_audio = audio.set_frame_rate(16000).set_channels(1)
            
            # 3. Exportar
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            processed_audio.export(output_path, format="wav")
            
            logger.info(f"Audio preprocesado y exportado a: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error en el preprocesamiento de audio: {e}")
            raise
