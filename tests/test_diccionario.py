"""
Validar estructura y contenido del diccionario de modismos
"""

import json
import os

def validate_diccionario(filepath):
    """Validar diccionario de modismos"""
    
    if not os.path.exists(filepath):
        print(f"❌ Archivo no encontrado: {filepath}")
        return ["Archivo no encontrado"]

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error de formato JSON: {e}")
            return ["JSON inválido"]
    
    errores = []
    
    # Validar metadata
    if 'metadata' not in data:
        errores.append("❌ Falta metadata")
    
    # Validar modismos
    if 'modismos' not in data:
        errores.append("❌ Falta array de modismos")
        return errores
    
    modismos = data['modismos']
    
    for i, mod in enumerate(modismos):
        # Campos obligatorios
        required = ['id', 'expresion_original', 'expresion_normalizada', 
                   'categoria', 'ejemplos']
        
        for field in required:
            if field not in mod:
                errores.append(f"❌ Modismo {i+1}: falta campo '{field}'")
        
        # Validar ejemplos (mínimo 2)
        if 'ejemplos' in mod and len(mod['ejemplos']) < 2:
            errores.append(f"⚠️ Modismo {i+1} ({mod.get('id', 'N/A')}): menos de 2 ejemplos")
    
    # Validar total
    if 'metadata' in data and len(modismos) != data['metadata'].get('total_expresiones', 0):
        errores.append(f"⚠️ Total declarado ({data['metadata'].get('total_expresiones')}) "
                      f"no coincide con real ({len(modismos)})")
    
    if not errores:
        print(f"✅ Diccionario válido: {len(modismos)} modismos")
    else:
        for err in errores:
            print(err)
    
    return errores

if __name__ == "__main__":
    validate_diccionario('data/diccionarios/modismos_es_CL_v1.0.json')
