import sys
import os
import logging

# Añadir raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers.audio_controller import AudioController
from src.services.stt_engine import STTEngine

# Configuración de logs para la prueba
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSTT")

def test_stt_flow():
    print("\n--- Iniciando Prueba de Flujo STT (P1) ---")
    
    audio_path = "data/audios_prueba/test_01_limpio.wav"
    output_temp = "data/audios_prueba/temp_whisper.wav"
    
    # 1. Verificar si existe el audio
    if not os.path.exists(audio_path):
        logger.warning(f"No se encontró el archivo de prueba en: {audio_path}")
        logger.info("La prueba no puede ejecutarse físicamente, pero el código está listo.")
        return

    try:
        # 2. Preprocesar
        print("1. Cargando y preprocesando audio...")
        controller = AudioController()
        audio = controller.load_audio(audio_path)
        processed_path = controller.preprocess_for_whisper(audio, output_temp)
        
        # 3. Transcribir
        print("2. Inicializando STTEngine (esto puede tardar la primera vez)...")
        engine = STTEngine(model_size="tiny")  # Usamos tiny para que el test sea rápido
        
        print("3. Transcribiendo...")
        transcription = engine.transcribe(processed_path)
        
        # 4. Resultados
        print("\n--- RESULTADOS ---")
        print(f"Texto completo: {transcription.texto_completo[:100]}...")
        print(f"Número de segmentos: {len(transcription.segmentos)}")
        print(f"Idioma: {transcription.idioma_detectado}")
        print(f"Duración: {transcription.duracion_procesada:.2f}s")
        
        if len(transcription.segmentos) > 0:
            print("✓ Flujo completado exitosamente.")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(output_temp):
            os.remove(output_temp)

if __name__ == "__main__":
    test_stt_flow()
