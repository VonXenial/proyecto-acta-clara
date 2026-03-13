# 02 - DICCIONARIO DE MODISMOS CHILENOS

**Documento:** Diccionario de Modismos  
**Versión:** 1.0  
**Fecha:** 12 marzo 2026  
**Crítico para:** P0 y P2  
**Tiempo estimado:** 3-4 horas (investigación + redacción)

---

## 📋 ÍNDICE

1. [Objetivo del Diccionario](#objetivo)
2. [Estructura JSON](#estructura-json)
3. [50 Modismos Chilenos Esenciales](#modismos-chilenos)
4. [20 Modismos Inglés (Opcional MVP)](#modismos-inglés)
5. [Categorías y Contextos](#categorías)
6. [Cómo Expandir el Diccionario](#expansión)
7. [Validación del Diccionario](#validación)

---

## 🎯 OBJETIVO DEL DICCIONARIO

### ¿Qué es un diccionario de modismos?

```
Base de datos estructurada que mapea expresiones coloquiales
(modismos regionales) a lenguaje formal/neutro.

Ejemplo:
"Me tinca" (CL) → "Me parece adecuado" (Formal)
```

### ¿Por qué es crítico para ActaClara?

```
1. ES TU DIFERENCIADOR TÉCNICO
   Otros sistemas transcriben, ActaClara NORMALIZA

2. DEMUESTRA INVESTIGACIÓN
   Shows que investigaste modismos reales chilenos

3. VALIDABLE EN DEMO
   Puedes mostrar detección en vivo durante defensa
```

---

## 📄 ESTRUCTURA JSON

### Archivo: `data/diccionarios/modismos_es_CL_v1.0.json`

```json
{
  "metadata": {
    "version": "1.0",
    "idioma": "es",
    "pais": "CL",
    "fecha_creacion": "2026-03-12",
    "autor": "Ian Leonardo Castro Contreras",
    "total_expresiones": 50,
    "fuentes": [
      "Diccionario de Chilenismos - Academia Chilena de la Lengua",
      "Observación directa en contextos empresariales chilenos"
    ]
  },
  "modismos": [
    {
      "id": "mod_001",
      "expresion_original": "me tinca",
      "expresion_normalizada": "me parece adecuado",
      "categoria": "opinion",
      "frecuencia": "alta",
      "contextos": ["reuniones", "decisiones", "sugerencias"],
      "ejemplos": [
        "Me tinca que deberíamos revisar el código",
        "No me tinca esa solución técnica"
      ],
      "variantes": ["me tinka", "le tinca", "nos tinca"],
      "nivel_formalidad": "informal",
      "notas": "Expresión muy común en contextos laborales chilenos"
    },
    {
      "id": "mod_002",
      "expresion_original": "al tiro",
      "expresion_normalizada": "inmediatamente",
      "categoria": "tiempo",
      "frecuencia": "muy_alta",
      "contextos": ["urgencia", "rapidez", "compromiso"],
      "ejemplos": [
        "Lo hago al tiro",
        "Necesitamos esa información al tiro"
      ],
      "variantes": ["altiro"],
      "nivel_formalidad": "informal",
      "notas": "Indica inmediatez, muy frecuente en contextos de urgencia"
    }
  ]
}
```

### Campos Obligatorios vs Opcionales

| Campo | Obligatorio | Propósito |
|-------|-------------|-----------|
| `id` | ✅ | Identificador único (mod_001, mod_002...) |
| `expresion_original` | ✅ | Modismo tal como se dice |
| `expresion_normalizada` | ✅ | Equivalente formal |
| `categoria` | ✅ | Tipo de modismo (ver lista abajo) |
| `ejemplos` | ✅ | Mínimo 2 frases de uso real |
| `frecuencia` | ⚠️ | muy_alta, alta, media, baja |
| `contextos` | ⚠️ | Dónde se usa (reuniones, email, etc) |
| `variantes` | ❌ | Opcional (otras formas de decirlo) |
| `notas` | ❌ | Opcional (contexto adicional) |

---

## 🇨🇱 50 MODISMOS CHILENOS ESENCIALES

### Categoría: OPINIÓN Y SUGERENCIAS (10)

```json
{
  "id": "mod_001",
  "expresion_original": "me tinca",
  "expresion_normalizada": "me parece adecuado",
  "categoria": "opinion",
  "ejemplos": [
    "Me tinca que deberíamos priorizar esa tarea",
    "No me tinca mucho ese enfoque"
  ]
},
{
  "id": "mod_002",
  "expresion_original": "cacho",
  "expresion_normalizada": "comprendo",
  "categoria": "opinion",
  "ejemplos": [
    "¿Cachai lo que te digo?",
    "No cacho bien el problema"
  ]
},
{
  "id": "mod_003",
  "expresion_original": "bacán",
  "expresion_normalizada": "excelente",
  "categoria": "opinion",
  "ejemplos": [
    "Esa solución está bacán",
    "Quedó bacán el diseño"
  ]
},
{
  "id": "mod_004",
  "expresion_original": "la raja",
  "expresion_normalizada": "muy bueno",
  "categoria": "opinion",
  "ejemplos": [
    "El resultado quedó la raja",
    "Esa presentación estuvo la raja"
  ]
},
{
  "id": "mod_005",
  "expresion_original": "filete",
  "expresion_normalizada": "de alta calidad",
  "categoria": "opinion",
  "ejemplos": [
    "Ese código está filete",
    "La documentación quedó filete"
  ]
},
{
  "id": "mod_006",
  "expresion_original": "más o menos nomás",
  "expresion_normalizada": "aproximadamente",
  "categoria": "opinion",
  "ejemplos": [
    "Son más o menos nomás 10 horas de trabajo",
    "Falta más o menos nomás una semana"
  ]
},
{
  "id": "mod_007",
  "expresion_original": "ni ahí",
  "expresion_normalizada": "no estoy de acuerdo",
  "categoria": "opinion",
  "ejemplos": [
    "Estoy ni ahí con ese cambio",
    "El equipo está ni ahí con trabajar el fin de semana"
  ]
},
{
  "id": "mod_008",
  "expresion_original": "igual",
  "expresion_normalizada": "de todas formas",
  "categoria": "opinion",
  "ejemplos": [
    "Igual podríamos intentarlo",
    "Igual es una buena idea"
  ]
},
{
  "id": "mod_009",
  "expresion_original": "peludo",
  "expresion_normalizada": "difícil",
  "categoria": "opinion",
  "ejemplos": [
    "Ese bug está peludo",
    "La integración va a estar peluda"
  ]
},
{
  "id": "mod_010",
  "expresion_original": "choro",
  "expresion_normalizada": "impresionante",
  "categoria": "opinion",
  "ejemplos": [
    "Esa arquitectura está chora",
    "Quedó choro el sistema"
  ]
}
```

### Categoría: TIEMPO Y URGENCIA (10)

```json
{
  "id": "mod_011",
  "expresion_original": "al tiro",
  "expresion_normalizada": "inmediatamente",
  "categoria": "tiempo",
  "ejemplos": [
    "Lo hago al tiro",
    "Necesitamos esa respuesta al tiro"
  ]
},
{
  "id": "mod_012",
  "expresion_original": "altoque",
  "expresion_normalizada": "de inmediato",
  "categoria": "tiempo",
  "ejemplos": [
    "Respondo altoque",
    "Envíalo altoque"
  ]
},
{
  "id": "mod_013",
  "expresion_original": "al tiro que sí",
  "expresion_normalizada": "por supuesto",
  "categoria": "tiempo",
  "ejemplos": [
    "¿Puedes revisar esto? Al tiro que sí",
    "¿Vamos a la reunión? Al tiro que sí"
  ]
},
{
  "id": "mod_014",
  "expresion_original": "recién",
  "expresion_normalizada": "hace poco",
  "categoria": "tiempo",
  "ejemplos": [
    "Recién terminé el reporte",
    "Recién me enteré del cambio"
  ]
},
{
  "id": "mod_015",
  "expresion_original": "hace rato",
  "expresion_normalizada": "hace tiempo",
  "categoria": "tiempo",
  "ejemplos": [
    "Eso lo implementamos hace rato",
    "Hace rato que no revisamos esa sección"
  ]
},
{
  "id": "mod_016",
  "expresion_original": "nunca en la vida",
  "expresion_normalizada": "jamás",
  "categoria": "tiempo",
  "ejemplos": [
    "Nunca en la vida había visto ese error",
    "Nunca en la vida lo voy a aprobar así"
  ]
},
{
  "id": "mod_017",
  "expresion_original": "cuando las ranas críen pelo",
  "expresion_normalizada": "nunca",
  "categoria": "tiempo",
  "ejemplos": [
    "Ese proyecto se va a terminar cuando las ranas críen pelo",
    "Van a arreglar eso cuando las ranas críen pelo"
  ]
},
{
  "id": "mod_018",
  "expresion_original": "en una de esas",
  "expresion_normalizada": "tal vez",
  "categoria": "tiempo",
  "ejemplos": [
    "En una de esas nos aprueban el presupuesto",
    "En una de esas funciona la solución"
  ]
},
{
  "id": "mod_019",
  "expresion_original": "piola",
  "expresion_normalizada": "tranquilo",
  "categoria": "tiempo",
  "ejemplos": [
    "Hagámoslo piola no más",
    "Vamos piola con los cambios"
  ]
},
{
  "id": "mod_020",
  "expresion_original": "de una",
  "expresion_normalizada": "enseguida",
  "categoria": "tiempo",
  "ejemplos": [
    "Lo hago de una",
    "De una te envío el archivo"
  ]
}
```

### Categoría: ACUERDO Y CONFIRMACIÓN (10)

```json
{
  "id": "mod_021",
  "expresion_original": "ya po",
  "expresion_normalizada": "de acuerdo",
  "categoria": "acuerdo",
  "ejemplos": [
    "Ya po, hagámoslo así",
    "Ya po, nos vemos mañana"
  ]
},
{
  "id": "mod_022",
  "expresion_original": "dale",
  "expresion_normalizada": "conforme",
  "categoria": "acuerdo",
  "ejemplos": [
    "Dale, procedemos con el plan",
    "Dale con esa solución"
  ]
},
{
  "id": "mod_023",
  "expresion_original": "listo",
  "expresion_normalizada": "entendido",
  "categoria": "acuerdo",
  "ejemplos": [
    "Listo, reviso y te confirmo",
    "Listo, queda claro"
  ]
},
{
  "id": "mod_024",
  "expresion_original": "obvio",
  "expresion_normalizada": "evidentemente",
  "categoria": "acuerdo",
  "ejemplos": [
    "Obvio que vamos a cumplir el plazo",
    "Obvio, eso lo sabemos todos"
  ]
},
{
  "id": "mod_025",
  "expresion_original": "nica",
  "expresion_normalizada": "de ninguna manera",
  "categoria": "acuerdo",
  "ejemplos": [
    "Nica vamos a terminar a tiempo",
    "Nica me comprometo con esa fecha"
  ]
},
{
  "id": "mod_026",
  "expresion_original": "en volá",
  "expresion_normalizada": "quizás",
  "categoria": "acuerdo",
  "ejemplos": [
    "En volá lo terminamos hoy",
    "En volá funciona así"
  ]
},
{
  "id": "mod_027",
  "expresion_original": "puede ser",
  "expresion_normalizada": "es posible",
  "categoria": "acuerdo",
  "ejemplos": [
    "Puede ser que tengamos que cambiar el enfoque",
    "Puede ser, habría que validarlo"
  ]
},
{
  "id": "mod_028",
  "expresion_original": "sale",
  "expresion_normalizada": "aceptado",
  "categoria": "acuerdo",
  "ejemplos": [
    "Sale, hacemos deploy el viernes",
    "Sale, coordinamos para mañana"
  ]
},
{
  "id": "mod_029",
  "expresion_original": "sipo",
  "expresion_normalizada": "sí",
  "categoria": "acuerdo",
  "ejemplos": [
    "Sipo, eso es lo que necesitamos",
    "Sipo, tiene sentido"
  ]
},
{
  "id": "mod_030",
  "expresion_original": "nopo",
  "expresion_normalizada": "no",
  "categoria": "acuerdo",
  "ejemplos": [
    "Nopo, esa no es la solución",
    "Nopo, no funciona así"
  ]
}
```

### Categoría: ACCIONES Y TAREAS (10)

```json
{
  "id": "mod_031",
  "expresion_original": "cachar",
  "expresion_normalizada": "entender",
  "categoria": "accion",
  "ejemplos": [
    "Hay que cachar bien el requerimiento",
    "No cachamos el bug todavía"
  ]
},
{
  "id": "mod_032",
  "expresion_original": "pega",
  "expresion_normalizada": "trabajo",
  "categoria": "accion",
  "ejemplos": [
    "Tenemos harta pega pendiente",
    "Esa pega está complicada"
  ]
},
{
  "id": "mod_033",
  "expresion_original": "cachar la onda",
  "expresion_normalizada": "comprender la situación",
  "categoria": "accion",
  "ejemplos": [
    "Cacha la onda con el cliente",
    "Hay que cachar la onda de lo que quieren"
  ]
},
{
  "id": "mod_034",
  "expresion_original": "echar una mano",
  "expresion_normalizada": "ayudar",
  "categoria": "accion",
  "ejemplos": [
    "¿Me echai una mano con esto?",
    "Necesitamos que alguien nos eche una mano"
  ]
},
{
  "id": "mod_035",
  "expresion_original": "mandarse un condoro",
  "expresion_normalizada": "cometer un error",
  "categoria": "accion",
  "ejemplos": [
    "Nos mandamos un condoro con ese deploy",
    "Se mandó un condoro al borrar la base de datos"
  ]
},
{
  "id": "mod_036",
  "expresion_original": "hacer la pega",
  "expresion_normalizada": "realizar el trabajo",
  "categoria": "accion",
  "ejemplos": [
    "Hay que hacer la pega bien",
    "Hicimos la pega en tiempo récord"
  ]
},
{
  "id": "mod_037",
  "expresion_original": "pasarse rollos",
  "expresion_normalizada": "preocuparse excesivamente",
  "categoria": "accion",
  "ejemplos": [
    "No te pases rollos con el deadline",
    "Se está pasando rollos con el código"
  ]
},
{
  "id": "mod_038",
  "expresion_original": "dar bote",
  "expresion_normalizada": "fallar",
  "categoria": "accion",
  "ejemplos": [
    "El servidor dio bote",
    "La integración dio bote en producción"
  ]
},
{
  "id": "mod_039",
  "expresion_original": "caer el veinte",
  "expresion_normalizada": "comprender",
  "categoria": "accion",
  "ejemplos": [
    "Recién me cayó el veinte de lo que querían",
    "Le va a caer el veinte cuando vea el resultado"
  ]
},
{
  "id": "mod_040",
  "expresion_normalizada": "dejar la escoba",
  "expresion_original": "causar desorden",
  "categoria": "accion",
  "ejemplos": [
    "Ese refactoring dejó la escoba en el código",
    "Van a dejar la escoba si hacen ese cambio"
  ]
}
```

### Categoría: EVALUACIÓN Y PROBLEMAS (10)

```json
{
  "id": "mod_041",
  "expresion_original": "fome",
  "expresion_normalizada": "aburrido",
  "categoria": "evaluacion",
  "ejemplos": [
    "Esa tarea es fome",
    "La reunión estuvo fome"
  ]
},
{
  "id": "mod_042",
  "expresion_original": "latero",
  "expresion_normalizada": "molesto",
  "categoria": "evaluacion",
  "ejemplos": [
    "Ese proceso es latero",
    "Qué latero tener que hacerlo manual"
  ]
},
{
  "id": "mod_043",
  "expresion_original": "chanta",
  "expresion_normalizada": "poco confiable",
  "categoria": "evaluacion",
  "ejemplos": [
    "Ese proveedor es chanta",
    "La solución quedó media chanta"
  ]
},
{
  "id": "mod_044",
  "expresion_original": "al lote",
  "expresion_normalizada": "de manera aproximada",
  "categoria": "evaluacion",
  "ejemplos": [
    "Lo hicieron al lote",
    "Ese cálculo está hecho al lote"
  ]
},
{
  "id": "mod_045",
  "expresion_original": "cahuín",
  "expresion_normalizada": "problema",
  "categoria": "evaluacion",
  "ejemplos": [
    "Se armó un cahuín con ese bug",
    "Hay cahuín con el cliente"
  ]
},
{
  "id": "mod_046",
  "expresion_original": "cagazo",
  "expresion_normalizada": "error grave",
  "categoria": "evaluacion",
  "ejemplos": [
    "Nos mandamos un cagazo con ese release",
    "Ese fue un cagazo monumental"
  ]
},
{
  "id": "mod_047",
  "expresion_original": "penca",
  "expresion_normalizada": "de mala calidad",
  "categoria": "evaluacion",
  "ejemplos": [
    "Esa API está penca",
    "El diseño quedó penca"
  ]
},
{
  "id": "mod_048",
  "expresion_original": "pencazo",
  "expresion_normalizada": "muy malo",
  "categoria": "evaluacion",
  "ejemplos": [
    "Ese código es un pencazo",
    "El resultado fue pencazo"
  ]
},
{
  "id": "mod_049",
  "expresion_original": "quedó como las huevas",
  "expresion_normalizada": "resultado deficiente",
  "categoria": "evaluacion",
  "ejemplos": [
    "La implementación quedó como las huevas",
    "El deploy quedó como las huevas"
  ]
},
{
  "id": "mod_050",
  "expresion_original": "pa la cagá",
  "expresion_normalizada": "muy mal",
  "categoria": "evaluacion",
  "ejemplos": [
    "El servidor está pa la cagá",
    "La situación está pa la cagá"
  ]
}
```

---

## 🇺🇸 20 MODISMOS INGLÉS (OPCIONAL PARA MVP)

### Archivo: `data/diccionarios/modismos_en_US_v1.0.json`

**Nota:** Solo implementar si sobra tiempo post P2

```json
{
  "id": "mod_en_001",
  "expresion_original": "gonna",
  "expresion_normalizada": "going to",
  "categoria": "contraccion",
  "ejemplos": [
    "We're gonna deploy on Friday",
    "I'm gonna review the code"
  ]
},
{
  "id": "mod_en_002",
  "expresion_original": "wanna",
  "expresion_normalizada": "want to",
  "categoria": "contraccion",
  "ejemplos": [
    "Do you wanna discuss this?",
    "I wanna clarify the requirements"
  ]
}
```

*(Resto de 18 modismos similares - expandir solo si es necesario)*

---

## 🏷️ CATEGORÍAS Y CONTEXTOS

### Categorías Definidas

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| `opinion` | Expresiones de parecer | me tinca, bacán, filete |
| `tiempo` | Referencias temporales | al tiro, recién, hace rato |
| `acuerdo` | Confirmaciones/negaciones | ya po, dale, nica |
| `accion` | Acciones y tareas | cachar, pega, hacer la pega |
| `evaluacion` | Juicios de valor | fome, latero, penca |

### Contextos de Uso

```json
"contextos": [
  "reuniones",      // Usado en reuniones presenciales
  "email",          // Aparece en correos informales
  "chat",           // Mensajería instantánea
  "presentaciones", // Exposiciones orales
  "decisiones",     // Toma de decisiones
  "urgencia",       // Situaciones urgentes
  "evaluacion"      // Evaluación de resultados
]
```

---

## 📈 CÓMO EXPANDIR EL DICCIONARIO

### Post-Defensa (Versión 2.0)

```python
# Script para agregar modismos desde feedback
# Archivo: scripts/add_modismo.py

import json
from datetime import datetime

def add_modismo(expresion_original, expresion_normalizada, categoria):
    """Agregar modismo al diccionario"""
    
    with open('data/diccionarios/modismos_es_CL_v1.0.json', 'r') as f:
        diccionario = json.load(f)
    
    nuevo_id = f"mod_{len(diccionario['modismos']) + 1:03d}"
    
    nuevo_modismo = {
        "id": nuevo_id,
        "expresion_original": expresion_original,
        "expresion_normalizada": expresion_normalizada,
        "categoria": categoria,
        "ejemplos": [],
        "fecha_agregado": datetime.now().isoformat()
    }
    
    diccionario['modismos'].append(nuevo_modismo)
    diccionario['metadata']['total_expresiones'] += 1
    
    with open('data/diccionarios/modismos_es_CL_v1.0.json', 'w') as f:
        json.dump(diccionario, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Agregado: {expresion_original} → {expresion_normalizada}")
```

---

## ✅ VALIDACIÓN DEL DICCIONARIO

### Script de Validación

**Archivo:** `tests/test_diccionario.py`

```python
"""
Validar estructura y contenido del diccionario de modismos
"""

import json

def validate_diccionario(filepath):
    """Validar diccionario de modismos"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
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
            errores.append(f"⚠️ Modismo {i+1}: menos de 2 ejemplos")
    
    # Validar total
    if len(modismos) != data['metadata']['total_expresiones']:
        errores.append(f"⚠️ Total declarado ({data['metadata']['total_expresiones']}) "
                      f"no coincide con real ({len(modismos)})")
    
    if not errores:
        print(f"✅ Diccionario válido: {len(modismos)} modismos")
    else:
        for err in errores:
            print(err)
    
    return errores

if __name__ == "__main__":
    validate_diccionario('data/diccionarios/modismos_es_CL_v1.0.json')
```

---

## 📋 CHECKLIST DE FINALIZACIÓN

- [ ] Archivo `modismos_es_CL_v1.0.json` creado
- [ ] 50 modismos chilenos documentados
- [ ] Cada modismo tiene mínimo 2 ejemplos
- [ ] Metadata completa (versión, fecha, autor)
- [ ] Script de validación ejecutado exitosamente
- [ ] Categorías asignadas correctamente

---

## 🎯 PRÓXIMO PASO

**→ Leer `03_P0_ARQUITECTURA_BASE.md`**

Con el diccionario listo, puedes empezar la implementación de la arquitectura base del sistema.

---

**Versión:** 1.0  
**Estado:** ✅ Plantilla lista para implementar  
**Modismos documentados:** 50 (español CL) + 2 ejemplos (inglés)  
**Tiempo de creación estimado:** 3-4 horas
