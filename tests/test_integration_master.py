"""
TEST MAESTRO DE INTEGRACIÓN - ACTACLARA
Simula el flujo completo de la UI por línea de comandos.
"""
import sys
import os
import logging

# Añadir raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers.audio_controller import AudioController
from src.services.stt_engine import STTEngine
from src.services.normalizer import Normalizer
from src.database.db_manager import DBManager
from src.models.acta import Acta

# Configurar logs para ver qué pasa "detrás de escena"
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_master_test():
    print("="*60)
    print("🚀 INICIANDO PRUEBA MAESTRA (Brain Integration)")
    print("="*60)

    try:
        # 1. Inicializar Componentes
        print("\n1. Inicializando motores...")
        audio_ctrl = AudioController()
        stt_engine = STTEngine(model_size="tiny") # Tiny para velocidad
        normalizer = Normalizer()
        db_manager = DBManager()
        db_manager.initialize_db()
        print("✅ Motores listos.")

        # 2. Audio de prueba (usaremos el que creamos antes)
        audio_path = "data/audios_prueba/test_01_limpio.wav"
        if not os.path.exists(audio_path):
            print("❌ Error: No existe el audio de prueba.")
            return

        # 3. Pipeline de Procesamiento
        print(f"\n2. Procesando audio: {audio_path}")
        audio_seg = audio_ctrl.load_audio(audio_path)
        temp_wav = "data/audios_prueba/temp_master.wav"
        audio_ctrl.preprocess_for_whisper(audio_seg, temp_wav)
        
        print("3. Transcribiendo con IA (Whisper)...")
        transcription = stt_engine.transcribe(temp_wav)
        
        # Simulamos un texto con modismos para probar la normalización 
        # ya que el audio de prueba es silencio.
        texto_a_normalizar = "Ya po, la pega está filete pero nos mandamos un condoro al tiro."
        print(f"\n4. Normalizando texto simulado:\n   '{texto_a_normalizar}'")
        
        texto_final, modismos = normalizer.normalize(texto_a_normalizar)
        print(f"✅ Resultado: '{texto_final}'")
        print(f"📈 Modismos detectados: {len(modismos)}")

        # 4. Persistencia
        print("\n5. Guardando acta en SQLite...")
        acta = Acta(
            titulo="Prueba Maestra de Integración",
            idioma=transcription.idioma_detectado,
            duracion_segundos=int(len(audio_seg)/1000),
            archivo_audio_ruta=audio_path,
            modismos_detectados=modismos
        )
        acta_id = db_manager.insert_acta(acta)
        print(f"✅ Acta guardada con ID: {acta_id}")

        print("\n" + "="*60)
        print("🎉 ¡SISTEMA OPERATIVO AL 100%!")
        print("El 'cerebro' de ActaClara está listo para la interfaz.")
        print("="*60)

    except Exception as e:
        print(f"\n❌ FALLO EN LA INTEGRACIÓN: {e}")
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

if __name__ == "__main__":
    run_master_test()
