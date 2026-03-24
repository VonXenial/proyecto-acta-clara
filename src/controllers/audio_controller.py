import os
import logging
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# Configurar el logger
logger = logging.getLogger("AudioController")

class AudioController:
    """
    Controlador para el preprocesamiento de audio y grabación en vivo.
    """
    
    def __init__(self, ffmpeg_path: str = "bin/ffmpeg.exe"):
        abs_ffmpeg_path = os.path.abspath(ffmpeg_path)
        if os.path.exists(abs_ffmpeg_path):
            AudioSegment.converter = abs_ffmpeg_path
        
        self._recording = False
        self._paused = False
        self._frames = []
        self._sample_rate = 16000
        self._stream = None

    def get_microphones(self):
        """Devuelve una lista de nombres de micrófonos disponibles."""
        devices = sd.query_devices()
        mics = []
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                mics.append(f"{i}: {d['name']}")
        return mics

    def start_recording(self, device_index=None):
        """Inicia la captura de audio."""
        self._recording = True
        self._paused = False
        self._frames = []
        
        def callback(indata, frames, time, status):
            if self._recording and not self._paused:
                self._frames.append(indata.copy())
        
        try:
            self._stream = sd.InputStream(samplerate=self._sample_rate, channels=1, 
                                          callback=callback, device=device_index)
            self._stream.start()
            logger.info(f"Grabación iniciada en dispositivo {device_index}")
        except Exception as e:
            logger.error(f"Error al iniciar grabación: {e}")
            raise

    def pause_recording(self):
        """Pausa la captura actual."""
        self._paused = True
        logger.info("Grabación pausada.")

    def resume_recording(self):
        """Reanuda la captura."""
        self._paused = False
        logger.info("Grabación reanudada.")

    def stop_recording(self, output_path: str) -> str:
        """Detiene y guarda el archivo."""
        if not self._stream: return ""
        self._recording = False
        self._stream.stop()
        self._stream.close()
        
        if self._frames:
            recording = np.concatenate(self._frames, axis=0)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            wav.write(output_path, self._sample_rate, recording)
            return output_path
        return ""

    def load_audio(self, file_path: str) -> AudioSegment:
        return AudioSegment.from_file(file_path)

    def preprocess_for_whisper(self, audio: AudioSegment, output_path: str) -> str:
        processed_audio = audio.set_frame_rate(16000).set_channels(1)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        processed_audio.export(output_path, format="wav")
        return output_path
