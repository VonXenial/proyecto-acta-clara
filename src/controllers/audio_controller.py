import os
import logging
from pydub import AudioSegment # type: ignore
import sounddevice as sd # type: ignore
import numpy as np # type: ignore
import scipy.io.wavfile as wav # type: ignore
from typing import Optional, List, Any

# Configurar el logger
logger = logging.getLogger("AudioController")

class AudioController:
    """
    Controlador para el preprocesamiento de audio y grabación en vivo.
    """
    
    def __init__(self, ffmpeg_path: str = "bin/ffmpeg.exe"):
        abs_ffmpeg_path = os.path.abspath(ffmpeg_path)
        abs_bin_dir = os.path.dirname(abs_ffmpeg_path)
        
        # Configurar pydub
        if os.path.exists(abs_ffmpeg_path):
            AudioSegment.converter = abs_ffmpeg_path
            # También configurar ffprobe si existe
            ffprobe_path = os.path.join(abs_bin_dir, "ffprobe.exe")
            if os.path.exists(ffprobe_path):
                # Pydub busca ffprobe en el sistema, pero podemos ayudarlo añadiendo al path temporalmente
                os.environ["PATH"] += os.pathsep + abs_bin_dir
        
        self._recording = False
        self._paused = False
        self._frames = []
        self._sample_rate = 16000
        self._stream: Optional[sd.InputStream] = None
        
        self._playback_stream: Optional[sd.OutputStream] = None
        self._playback_data: Optional[np.ndarray] = None
        self._playback_pos = 0
        self._playback_active = False
        self._sample_rate_playback = 44100  # sample rate actual del audio cargado
        self._volume = 1.0
        
        # Diagnóstico inicial
        self._print_hardware_info()

    def _print_hardware_info(self):
        """Imprime información de hardware para diagnóstico."""
        print("\n--- AudioController: Diagnóstico de Hardware ---")
        try:
            input_devs = self.get_microphones()
            output_devs = self.get_output_devices()
            print(f"Micrófonos detectados: {len(input_devs)}")
            print(f"Salidas detectadas: {len(output_devs)}")
            for d in output_devs:
                print(f"  > {d}")
            
            default_out = sd.query_devices(kind='output')
            print(f"Salida predeterminada: {default_out['name'] if default_out else 'Ninguna'}")
        except Exception as e:
            print(f"Error en diagnóstico: {e}")
        print("-----------------------------------------------\n")

    def get_output_devices(self):
        """Devuelve una lista de nombres de salidas (parlantes) disponibles."""
        devices = sd.query_devices()
        outs = []
        for i, d in enumerate(devices):
            if d['max_output_channels'] > 0:
                outs.append(f"{i}: {d['name']}")
        return outs

    def get_microphones(self):
        """Devuelve una lista de nombres de micrófonos disponibles."""
        devices = sd.query_devices()
        mics = []
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                mics.append(f"{i}: {d['name']}")
        return mics

    def set_sample_rate(self, rate: int):
        """Ajusta la tasa de muestreo para futuras grabaciones."""
        self._sample_rate = rate
        logger.info(f"Tasa de muestreo configurada a: {rate}Hz")

    def start_recording(self, device_index=None):
        """Inicia la captura de audio."""
        self._recording = True
        self._paused = False
        self._frames = []
        
        def callback(indata, frames, time, status):
            if self._recording and not self._paused:
                self._frames.append(indata.copy())
        
        try:
            logger.info(f"Iniciando grabación... SR={self._sample_rate}, Device={device_index}")
            self._stream = sd.InputStream(samplerate=self._sample_rate, channels=1, 
                                          callback=callback, device=device_index)
            if self._stream:
                self._stream.start() # type: ignore
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
        if not self._stream:
            return ""
        self._recording = False
        if self._stream:
            self._stream.stop() # type: ignore
            self._stream.close() # type: ignore
            self._stream = None
        
        if self._frames:
            recording = np.concatenate(self._frames, axis=0)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            wav.write(output_path, self._sample_rate, recording) # type: ignore
            return output_path
        return ""

    def load_audio(self, file_path: str) -> AudioSegment:
        return AudioSegment.from_file(file_path)

    def preprocess_for_whisper(self, audio: AudioSegment, output_path: str) -> str:
        processed_audio = audio.set_frame_rate(16000).set_channels(1)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        processed_audio.export(output_path, format="wav")
        return output_path

    # --- Playback Methods ---

    def load_playback_audio(self, file_path: str):
        """Prepara un archivo para reproducción.
        
        Intenta cargar WAV directamente con scipy (sin FFMPEG) y
        usa pydub como fallback para MP3/M4A.
        """
        try:
            logger.info(f"Cargando para playback: {file_path}")
            if not os.path.exists(file_path):
                logger.error(f"Archivo no existe: {file_path}")
                return 0
            
            ext = os.path.splitext(file_path)[1].lower()
            
            # Ruta rápida para WAV: usar scipy directamente (sin FFMPEG)
            if ext == ".wav":
                try:
                    sample_rate, data = wav.read(file_path)
                    # Convertir a mono si es estéreo
                    if data.ndim > 1:
                        data = data.mean(axis=1)
                    # Normalizar a float32 [-1, 1]
                    if data.dtype == np.int16:
                        data = data.astype(np.float32) / 32768.0
                    elif data.dtype == np.int32:
                        data = data.astype(np.float32) / 2147483648.0
                    elif data.dtype != np.float32:
                        data = data.astype(np.float32)
                    # Resamplear a 44100 si es necesario
                    if sample_rate != 44100:
                        try:
                            import scipy.signal as sig
                            num_samples = int(len(data) * 44100 / sample_rate)
                            data = sig.resample(data, num_samples)
                        except Exception:
                            pass  # Usar sample_rate original si falla el resample
                        sample_rate = 44100
                    self._playback_data = data
                    self._playback_pos = 0
                    self._playback_active = False
                    self._sample_rate_playback = sample_rate
                    duration = len(data) / sample_rate
                    logger.info(f"WAV cargado con scipy. Duración: {duration:.2f}s")
                    return duration
                except Exception as wav_err:
                    logger.warning(f"scipy falló para WAV, intentando pydub: {wav_err}")
            
            # Fallback: pydub (requiere FFMPEG para MP3/M4A)
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_frame_rate(44100).set_channels(1)
            self._playback_data = np.array(audio.get_array_of_samples(), dtype="float32")
            if audio.sample_width == 2:
                self._playback_data /= 32768.0
            elif audio.sample_width == 4:
                self._playback_data /= 2147483648.0
            self._playback_pos = 0
            self._playback_active = False
            self._sample_rate_playback = 44100
            duration = len(self._playback_data) / 44100.0
            logger.info(f"Audio cargado con pydub. Duración: {duration:.2f}s")
            return duration
        except Exception as e:
            logger.error(f"Error cargando audio '{file_path}': {e}")
            return 0

    def play_audio(self, start_pos_seg: float = 0):
        """Inicia o reanuda la reproducción desde una posición en segundos."""
        if self._playback_data is None:
            logger.warning("Sin datos para reproducir.")
            return
        
        if self._playback_active:
            self.stop_playback()
            
        self._playback_pos = int(start_pos_seg * self._sample_rate_playback)
        self._playback_active = True
        logger.info(f"Play desde {start_pos_seg:.2f}s")
        
        def callback(outdata, frames, time, status):
            if not self._playback_active:
                raise sd.CallbackStop()
                
            data = self._playback_data
            if data is None:
                raise sd.CallbackStop()
                
            chunk = data[self._playback_pos : self._playback_pos + frames]
            
            if len(chunk) == 0:
                self._playback_active = False
                raise sd.CallbackStop()

            # Adaptar a canales de salida (ej. Stereo)
            channels = outdata.shape[1]
            if len(chunk) < frames:
                # Caso final del audio
                padded = np.zeros((frames,))
                padded[:len(chunk)] = chunk * self._volume
                for c in range(channels):
                    outdata[:, c] = padded
                self._playback_active = False
                raise sd.CallbackStop()
            else:
                # Reproducción normal
                for c in range(channels):
                    outdata[:, c] = chunk * self._volume
                self._playback_pos += frames

        try:
            self._playback_stream = sd.OutputStream(
                samplerate=self._sample_rate_playback, 
                channels=None, # Auto-detectar
                callback=callback
            )
            if self._playback_stream:
                self._playback_stream.start() # type: ignore
        except Exception as e:
            logger.error(f"Error stream: {e}")
            self._playback_active = False

    def stop_playback(self):
        """Detiene la reproducción."""
        self._playback_active = False
        if self._playback_stream:
            try:
                self._playback_stream.stop() # type: ignore
                self._playback_stream.close() # type: ignore
            except Exception:
                pass
            self._playback_stream = None

    def get_playback_pos(self) -> float:
        """Devuelve la posición actual de reproducción en segundos."""
        return self._playback_pos / 44100.0

    def set_volume(self, volume: float):
        """Ajusta el volumen (0.0 a 1.0)."""
        self._volume = max(0.0, min(1.0, volume))

    def is_playing(self) -> bool:
        return self._playback_active
