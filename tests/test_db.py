import sys
import os

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.db_manager import DBManager
from src.models.acta import Acta
from src.models.modismo import ModismoDetectado

def test_persistence():
    print("--- Iniciando Prueba de Persistencia ---")
    db = DBManager()
    
    # 1. Inicializar DB
    print("1. Inicializando base de datos...")
    db.initialize_db()
    
    # 2. Crear Acta de prueba
    print("2. Creando acta de prueba...")
    modismo1 = ModismoDetectado(
        expresion_original="fome",
        expresion_normalizada="aburrido",
        posicion_inicio=10,
        posicion_fin=14,
        accion_usuario="ACEPTADA"
    )
    
    acta_test = Acta(
        titulo="Reunión Semanal de Prueba",
        idioma="es-CL",
        duracion_segundos=120,
        archivo_audio_ruta="data/audio/prueba.mp3",
        archivo_docx_ruta="outputs/prueba.docx",
        wer_medido=0.05,
        modismos_detectados=[modismo1]
    )
    
    # 3. Insertar Acta
    print("3. Insertando acta...")
    acta_id = db.insert_acta(acta_test)
    print(f"ID generado: {acta_id}")
    
    # 4. Recuperar Acta
    print("4. Recuperando acta...")
    acta_recuperada = db.get_acta_by_id(acta_id)
    
    if acta_recuperada:
        print(f"✓ Acta recuperada: {acta_recuperada.titulo}")
        print(f"✓ Fecha: {acta_recuperada.fecha_creacion}")
        print(f"✓ Modismos detectados: {len(acta_recuperada.modismos_detectados)}")
        for m in acta_recuperada.modismos_detectados:
            print(f"  - '{m.expresion_original}' -> '{m.expresion_normalizada}'")
        
        # Verificaciones
        assert acta_recuperada.titulo == acta_test.titulo
        assert len(acta_recuperada.modismos_detectados) == 1
        assert acta_recuperada.modismos_detectados[0].expresion_original == "fome"
        print("\n--- PRUEBA EXITOSA ---")
    else:
        print("\n--- PRUEBA FALLIDA: No se pudo recuperar el acta ---")
        sys.exit(1)

if __name__ == "__main__":
    test_persistence()
