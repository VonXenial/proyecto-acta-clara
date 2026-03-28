import logging
import ctranslate2 # type: ignore
from faster_whisper import WhisperModel # type: ignore
from src.models.transcription import Transcription, TranscripcionSegmento # type: ignore
from src.services.normalizer import Normalizer # type: ignore

# Configurar el logger
logger = logging.getLogger("STTEngine")

class STTEngine:
    """
    Servicio de transcripción Speech-to-Text usando faster-whisper.
    Optimizado para modismos chilenos con integración al diccionario local.
    """
    
    def __init__(self, model_size: str = "small", device: str = "auto", compute_type: str = "auto", cpu_threads: int = 4):
        """
        Inicializa el modelo de Whisper con detección automática de hardware.
        """
        try:
            # 1. Detección automática de hardware
            actual_device = device
            if device == "auto":
                try:
                    if ctranslate2.get_cuda_device_count() > 0:
                        actual_device = "cuda"
                        logger.info("GPU detectada. Usando aceleración por hardware.")
                    else:
                        actual_device = "cpu"
                        logger.info("GPU no detectada. Usando modo CPU.")
                except Exception:
                    actual_device = "cpu"
            
            # 2. Selección inteligente de tipo de cómputo
            # GPU -> float16 (más rápido), CPU -> int8 (más eficiente en CPU)
            actual_compute = compute_type
            if compute_type == "auto":
                actual_compute = "float16" if actual_device == "cuda" else "int8"

            logger.info(f"Cargando modelo Whisper '{model_size}' en {actual_device} ({actual_compute}) con {cpu_threads} hilos...")
            
            try:
                self.model = WhisperModel(model_size, device=actual_device, compute_type=actual_compute, cpu_threads=cpu_threads)
            except Exception as e:
                if actual_device == "cuda":
                    logger.warning(f"Error al inicializar GPU ({e}). Intentando fallback a CPU...")
                    self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                else:
                    raise
            
            logger.info("Modelo de IA cargado exitosamente.")
            
            # Cargar diccionario de modismos para construir el prompt
            self.normalizer = Normalizer()
            self._build_prompt_from_dictionary()
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo Whisper: {e}")
            raise

    def _build_prompt_from_dictionary(self):
        """
        Construye un prompt inicial optimizado basado en el diccionario local.
        Este prompt guía a Whisper para reconocer mejor los modismos chilenos.
        """
        # Obtener todos los modismos del diccionario
        modismos_dict = self.normalizer.modismos_dict
        
        if not modismos_dict:
            logger.warning("Diccionario de modismos vacío. Usando prompt genérico.")
            self.chilean_prompt = self._get_fallback_prompt()
            return
        
        # Extraer solo expresiones originales (las que Whisper debe reconocer)
        expresiones = [m["expresion_original"] for m in modismos_dict[:50]]  # Top 50 más comunes
        
        # Construir prompt estructurado
        self.chilean_prompt = self._construct_optimized_prompt(expresiones)
        logger.info(f"Prompt construido con {len(expresiones)} modismos del diccionario local.")

    def _construct_optimized_prompt(self, expresiones: list) -> str:
        """
        Construye un prompt optimizado para Whisper.
        
        Estrategia:
        1. Contexto geográfico y lingüístico
        2. Palabras clave del dominio (reuniones, actas)
        3. Modismos frecuentes del diccionario
        4. Evitar alucinaciones con frases cortas y naturales
        
        Args:
            expresiones: Lista de modismos del diccionario local
            
        Returns:
            Prompt optimizado como string
        """
        # === PARTE 1: Contexto ===
        context = "Audio de una reunión de trabajo en Chile."
        
        # === PARTE 2: Vocabulario del dominio ===
        domain_vocab = [
            "reunión", "acta", "acuerdo", "tarea", "compromiso",
            "equipo", "proyecto", "discusión", "decisión", "objetivo"
        ]
        
        # === PARTE 3: Modismos chilenos prioritarios ===
        # Limitar a 30-40 palabras para no saturar el prompt
        top_modismos = expresiones[:30] if len(expresiones) > 30 else expresiones
        
        # === PARTE 4: Construcción del prompt ===
        # Whisper funciona mejor con frases naturales que con listas
        prompt_parts = [
            context,
            # Ejemplo de uso natural del vocabulario
            f"En la reunión se discutieron los acuerdos y tareas del proyecto.",
            # Integrar modismos de forma natural
            self._create_natural_sentence(top_modismos[:15]),
            # Segunda oración con más modismos
            self._create_natural_sentence(top_modismos[15:30]) if len(top_modismos) > 15 else ""
        ]
        
        # Unir con espacios, eliminar vacíos
        final_prompt = " ".join(filter(None, prompt_parts))
        
        # Limitar longitud total (Whisper tiene límite de ~224 tokens)
        if len(final_prompt) > 400:
            final_prompt = final_prompt[:400]
        
        logger.debug(f"Prompt final: {final_prompt}")
        return final_prompt

    def _create_natural_sentence(self, modismos: list) -> str:
        """
        Crea una frase natural usando los modismos proporcionados.
        
        Estrategia: Alternar entre diferentes estructuras para parecer natural.
        
        Args:
            modismos: Lista de expresiones a integrar
            
        Returns:
            Frase natural con los modismos
        """
        if not modismos:
            return ""
        
        # Templates de frases naturales
        templates = [
            "El equipo mencionó palabras como {words}.",
            "Se hablaron expresiones comunes: {words}.",
            "Durante la conversación dijeron {words}.",
        ]
        
        # Seleccionar template aleatoriamente (o rotar)
        import random
        template = random.choice(templates)
        
        # Unir modismos con comas naturalmente
        words_str = ", ".join(modismos[:10])  # Máximo 10 por frase
        
        return template.format(words=words_str)

    def _get_fallback_prompt(self) -> str:
        """
        Prompt de respaldo si no hay diccionario disponible.
        
        Returns:
            Prompt genérico optimizado para Chile
        """
        return (
            "Audio de una reunión de trabajo en Chile. "
            "El equipo mencionó palabras como weón, bacán, cachái, al tiro, "
            "pega, cachar, fome, la raja, pololo, piola, buena onda."
        )

    def transcribe(self, audio_path: str, language: str = None) -> Transcription:
        """
        Transcribe el archivo de audio y devuelve un objeto Transcription.
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Código de idioma ('es', 'en', None para auto-detectar)
            
        Returns:
            Objeto Transcription con texto completo y segmentos
        """
        try:
            logger.info(f"Iniciando transcripción de: {audio_path}")
            
            # Configuración optimizada de Whisper
            transcribe_params = {
                "beam_size": 5,  # Balance entre calidad y velocidad
                "best_of": 5,    # Mejora calidad (usa más recursos)
                "temperature": 0.0,  # Determinista, sin aleatoriedad
                "vad_filter": True,  # Filtro de actividad de voz
                "vad_parameters": {
                    "min_silence_duration_ms": 500,  # Pausas mínimas
                    "speech_pad_ms": 400,  # Padding para no cortar palabras
                },
                "initial_prompt": self.chilean_prompt,  # ← PROMPT OPTIMIZADO
                "word_timestamps": False,  # Desactivar si no necesitas timestamps por palabra
                "condition_on_previous_text": True,  # Usar contexto de segmentos anteriores
                "compression_ratio_threshold": 2.4,  # Detectar repeticiones (alucinaciones)
                "log_prob_threshold": -1.0,  # Filtrar segmentos de baja confianza
                "no_speech_threshold": 0.6,  # Umbral para detectar silencio
            }
            
            # Agregar idioma si se especifica
            if language:
                transcribe_params["language"] = language
            
            # Ejecutar transcripción
            segments, info = self.model.transcribe(audio_path, **transcribe_params)
            
            transcription_segments = []
            full_text = []
            total_confidence = 0.0
            import math
            
            for segment in segments:
                # Filtrar segmentos vacíos o muy cortos (posibles alucinaciones)
                text = segment.text.strip()
                if len(text) < 2:
                    continue
                
                # Calcular confianza del segmento (e^logprob)
                conf = math.exp(segment.avg_logprob)
                total_confidence += conf
                
                # Mapear a nuestro modelo de dominio
                transcription_segments.append(
                    TranscripcionSegmento(
                        texto=text,
                        inicio=segment.start,
                        fin=segment.end
                    )
                )
                full_text.append(text)
            
            avg_conf = (total_confidence / len(transcription_segments)) if transcription_segments else 0.0
            
            logger.info(
                f"Transcripción completada. "
                f"Idioma: {info.language} ({info.language_probability:.2%}). "
                f"Confianza Media: {avg_conf:.2%}. "
                f"Segmentos: {len(transcription_segments)}. "
                f"Duración: {info.duration:.2f}s"
            )
            
            return Transcription(
                texto_completo=" ".join(full_text),
                segmentos=transcription_segments,
                idioma_detectado=info.language,
                duracion_procesada=info.duration,
                confianza_media=avg_conf
            )
            
        except Exception as e:
            logger.error(f"Error durante la transcripción: {e}", exc_info=True)
            raise

    def update_prompt(self):
        """
        Actualiza el prompt cuando el diccionario de modismos cambia.
        Llamar después de agregar/editar modismos manualmente.
        """
        logger.info("Actualizando prompt con nuevo diccionario de modismos...")
        self.normalizer = Normalizer()  # Recargar diccionario
        self._build_prompt_from_dictionary()
        logger.info("Prompt actualizado exitosamente.")
