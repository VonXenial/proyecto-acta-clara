import sys
import os

# Añadir raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.normalizer import Normalizer

def test_normalization():
    print("\n--- Iniciando Prueba de Normalización (P2) ---")
    
    normalizer = Normalizer()
    
    # Frase de prueba solicitada
    frase = "Ya po, hagamos la pega al tiro que nos mandamos un condoro"
    print(f"Original: {frase}")
    
    texto_norm, encontrados = normalizer.normalize(frase)
    
    print(f"Normalizado: {texto_norm}")
    print(f"Modismos detectados: {len(encontrados)}")
    
    for m in encontrados:
        print(f"  - '{m.expresion_original}' ({m.posicion_inicio}:{m.posicion_fin}) -> '{m.expresion_normalizada}'")

    # Verificaciones básicas
    assert "de acuerdo" in texto_norm
    assert "trabajo" in texto_norm
    assert "inmediatamente" in texto_norm
    assert "error" in texto_norm
    
    # Probar solapamiento ("al tiro que sí" vs "al tiro")
    frase_overlap = "Al tiro que sí lo hago al tiro"
    print(f"\nOriginal (overlap): {frase_overlap}")
    texto_overlap_norm, encontrados_overlap = normalizer.normalize(frase_overlap)
    print(f"Normalizado: {texto_overlap_norm}")
    
    assert "por supuesto" in texto_overlap_norm
    assert "inmediatamente" in texto_overlap_norm
    
    print("\n✓ Todas las pruebas de normalización pasaron exitosamente.")

if __name__ == "__main__":
    test_normalization()
