# 08 - PROMPTS PARA GEMINI CLI - ESTRATEGIA MULTI-AGENTE

**Documento:** Prompts Gemini CLI  
**Versión:** 1.0  
**Fecha:** 12 marzo 2026  
**Para:** Google Antigravity + Open Agent Manager

---

## 📋 ÍNDICE

1. [Configuración de Gemini CLI](#configuración)
2. [Arquitectura Multi-Agente](#arquitectura)
3. [Prompts por Agente](#prompts-por-agente)
4. [Comandos Básicos](#comandos-básicos)
5. [Workflow de Desarrollo](#workflow)
6. [Gestión de Versiones .md](#gestión-de-versiones)

---

## ⚙️ CONFIGURACIÓN DE GEMINI CLI

### Instalación

```bash
# Con entorno virtual activado (venv)
pip install google-generativeai

# Verificar instalación
python -c "import google.generativeai as genai; print('✅ Gemini CLI listo')"
```

### Configurar API Key

```bash
# Crear archivo .env en raíz del proyecto
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env

# Agregar a .gitignore
echo ".env" >> .gitignore
```

### Script de Inicialización

**Archivo:** `scripts/gemini_init.py`

```python
"""
Inicialización de Gemini CLI para ActaClara
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configurar API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Modelos disponibles en Antigravity
MODELS = {
    'arquitecto': 'gemini-3.1-pro-high',
    'backend': 'gemini-3-flash',
    'ui': 'claude-sonnet-4.6-thinking',
    'debugger': 'gpt-oss-120b-medium',
}

def get_model(agent_name):
    """Obtener modelo configurado para un agente"""
    model_name = MODELS.get(agent_name, 'gemini-1.5-flash')
    return genai.GenerativeModel(model_name)

def test_connection():
    """Verificar conexión con Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Di: ActaClara listo")
        print(f"✅ Conexión exitosa: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

---

## 🏗️ ARQUITECTURA MULTI-AGENTE

### Estrategia de Especialización

```
┌─────────────────────────────────────────────────────────┐
│              ORQUESTADOR (Claude)                       │
│  - Define tareas en .md                                 │
│  - Revisa código generado                               │
│  - Actualiza documentación                              │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┬────────────┬────────────┐
       │                │            │            │
   ┌───▼───┐      ┌────▼────┐  ┌────▼────┐  ┌───▼────┐
   │AGENTE1│      │ AGENTE2 │  │ AGENTE3 │  │AGENTE4 │
   │Arqui  │      │ Backend │  │   UI    │  │ Debug  │
   │tecto  │      │         │  │         │  │        │
   └───────┘      └─────────┘  └─────────┘  └────────┘
```

### Roles y Responsabilidades

| Agente | Modelo | Especialización | Cuándo Usar |
|--------|--------|-----------------|-------------|
| **Arquitecto** | Gemini 1.5 Pro | Diseño de clases, estructura | Inicio de cada prototipo |
| **Backend** | Gemini 2.0 Flash | Código Python (STT, normalización) | P1, P2 |
| **UI** | Gemini 1.5 Pro | Tkinter, eventos, layouts | P3 |
| **Debugger** | Gemini 1.5 Flash | Análisis de errores, fixes | Cuando algo falla |

---

## 🤖 PROMPTS POR AGENTE

### 🏛️ AGENTE 1: ARQUITECTO

**Responsabilidad:** Diseñar estructura de clases y arquitectura

**Prompt Base:**

```text
Eres un arquitecto de software senior especializado en Python y diseño orientado a objetos.

CONTEXTO DEL PROYECTO:
- Nombre: ActaClara
- Objetivo: Transcripción de audio con normalización de modismos
- Stack: Python 3.10, faster-whisper, Tkinter, SQLite
- Patrón: MVC (Modelo-Vista-Controlador)

TAREA ACTUAL:
[Leer desde .md correspondiente]

INSTRUCCIONES:
1. Diseña las clases necesarias siguiendo principios SOLID
2. Define métodos públicos y privados claramente
3. Especifica tipos de retorno (type hints)
4. Considera extensibilidad futura
5. Genera solo la ESTRUCTURA (sin implementación completa)

FORMATO DE SALIDA:
```python
# Código con estructura de clases
# Incluir docstrings
# Sin implementación de métodos (solo pass)
```

RESTRICCIONES:
- Máximo 5 clases por módulo
- Nombres descriptivos en español
- Evitar herencia múltiple
- Preferir composición sobre herencia
```

**Ejemplo de Uso:**

```bash
python scripts/gemini_agent.py arquitecto "Diseña las clases para el motor de transcripción (P1)"
```

**Archivo:** `scripts/gemini_agent.py`

```python
"""
CLI para ejecutar agentes Gemini
"""

import sys
from gemini_init import get_model

def run_agent(agent_name, task_description):
    """Ejecutar agente con tarea específica"""
    
    # Cargar prompt base del agente
    prompts = {
        'arquitecto': open('prompts/arquitecto_base.txt').read(),
        'backend': open('prompts/backend_base.txt').read(),
        'ui': open('prompts/ui_base.txt').read(),
        'debugger': open('prompts/debugger_base.txt').read(),
    }
    
    prompt_base = prompts.get(agent_name, '')
    prompt_completo = f"{prompt_base}\n\nTAREA ESPECÍFICA:\n{task_description}"
    
    model = get_model(agent_name)
    response = model.generate_content(prompt_completo)
    
    print(f"\n{'='*60}")
    print(f"AGENTE: {agent_name.upper()}")
    print(f"{'='*60}\n")
    print(response.text)
    
    # Guardar resultado
    output_file = f"outputs/{agent_name}_{int(time.time())}.py"
    with open(output_file, 'w') as f:
        f.write(response.text)
    
    print(f"\n✅ Guardado en: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python gemini_agent.py [agente] [tarea]")
        print("Agentes: arquitecto, backend, ui, debugger")
        sys.exit(1)
    
    run_agent(sys.argv[1], sys.argv[2])
```

---

### 💻 AGENTE 2: BACKEND (CodeGen)

**Responsabilidad:** Implementar código Python funcional

**Prompt Base:**

```text
Eres un desarrollador Python senior con expertise en:
- Procesamiento de audio (pydub, FFmpeg)
- Modelos de ML (PyTorch, faster-whisper)
- Manejo de archivos y SQLite

CONTEXTO DEL PROYECTO:
- Nombre: ActaClara
- Stack: Python 3.10, faster-whisper, pydub, SQLite
- Patrón: MVC

TAREA ACTUAL:
[Leer desde .md correspondiente]

INSTRUCCIONES:
1. Implementa código FUNCIONAL y PROBADO
2. Incluye manejo de errores (try/except)
3. Agrega logging para debugging
4. Usa type hints en todos los métodos
5. Escribe docstrings estilo Google

FORMATO DE SALIDA:
```python
# Código completo con implementación
# Incluir imports necesarios
# Agregar ejemplos de uso en if __name__ == "__main__"
```

RESTRICCIONES:
- Solo usar librerías del requirements.txt
- Evitar dependencias adicionales
- Código debe funcionar en Windows/macOS/Linux
- Máximo 200 líneas por archivo
```

**Ejemplo de Uso:**

```bash
python scripts/gemini_agent.py backend "Implementa ControladorAudio con método load_audio(filepath) que use pydub"
```

---

### 🎨 AGENTE 3: UI SPECIALIST

**Responsabilidad:** Generar código Tkinter

**Prompt Base:**

```text
Eres un especialista en interfaces de usuario con Tkinter en Python.

CONTEXTO DEL PROYECTO:
- Nombre: ActaClara
- UI Framework: Tkinter (ya incluido en Python)
- Diseño: Minimalista, funcional, siguiendo mockups de documentación
- Colores: Azul #2E75B6, Verde #28A745, Naranja #FF8C00

TAREA ACTUAL:
[Leer desde .md correspondiente]

INSTRUCCIONES:
1. Genera código Tkinter funcional
2. Usa ttk para widgets modernos cuando sea posible
3. Implementa responsive layout (grid o pack)
4. Agrega tooltips y feedback visual
5. Maneja eventos (click, hover, key press)

FORMATO DE SALIDA:
```python
# Código Tkinter completo
# Incluir clase principal heredando de tk.Tk o tk.Frame
# Agregar método main() para ejecución
```

RESTRICCIONES:
- Solo Tkinter estándar (no ttkbootstrap u otros)
- Ventanas deben ser resizables
- Mínimo 1024x768px de resolución
- Accesibilidad: tamaño de fuente mínimo 10pt
```

**Ejemplo de Uso:**

```bash
python scripts/gemini_agent.py ui "Crea ventana principal con botón 'Importar Audio' y área de texto para transcripción"
```

---

### 🐛 AGENTE 4: DEBUGGER

**Responsabilidad:** Analizar y corregir errores

**Prompt Base:**

```text
Eres un experto en debugging de Python especializado en:
- Análisis de tracebacks
- Errores de dependencias (pip, imports)
- Problemas de compatibilidad OS
- Performance y memory leaks

CONTEXTO DEL PROYECTO:
- Nombre: ActaClara
- Stack: Python 3.10, faster-whisper, Tkinter, SQLite

ERROR REPORTADO:
[Pegar traceback completo aquí]

CÓDIGO RELACIONADO:
[Pegar snippet de código]

INSTRUCCIONES:
1. Identifica la causa raíz del error
2. Explica POR QUÉ ocurrió (no solo cómo arreglarlo)
3. Proporciona solución paso a paso
4. Ofrece alternativas si la hay
5. Sugiere cómo prevenir errores similares

FORMATO DE SALIDA:
## 🔍 DIAGNÓSTICO
[Explicación del problema]

## 🛠️ SOLUCIÓN
```python
# Código corregido
```

## 📋 PASOS
1. [Paso 1]
2. [Paso 2]
...

## 🚨 PREVENCIÓN
[Cómo evitar este error en futuro]
```

**Ejemplo de Uso:**

```bash
# Guardar error en archivo
echo "Traceback (most recent call last):
  File 'stt_engine.py', line 42
    model = WhisperModel('small')
ModuleNotFoundError: No module named 'faster_whisper'" > error.txt

# Ejecutar debugger
python scripts/gemini_agent.py debugger "$(cat error.txt)"
```

---

## 💻 COMANDOS BÁSICOS DE GEMINI CLI

### Comando 1: Generar Código desde .md

```bash
# Leer tarea desde documento .md y generar código
python scripts/md_to_code.py 04_P1_MOTOR_TRANSCRIPCION.md --agent backend
```

**Script:** `scripts/md_to_code.py`

```python
"""
Extrae tareas desde .md y genera código con Gemini
"""

import sys
import re
from gemini_agent import run_agent

def extract_task(md_file):
    """Extraer sección TAREA del .md"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar sección ## TAREA o similar
    match = re.search(r'## TAREA.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python md_to_code.py [archivo.md] --agent [nombre]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    agent = sys.argv[3] if len(sys.argv) > 3 else 'backend'
    
    task = extract_task(md_file)
    if task:
        run_agent(agent, task)
    else:
        print("❌ No se encontró sección TAREA en .md")
```

### Comando 2: Debugging Rápido

```bash
# Pasar error directamente
python scripts/gemini_agent.py debugger "Error: ModuleNotFoundError: No module named 'faster_whisper'"
```

### Comando 3: Review de Código

```bash
# Pedir review de código generado
python scripts/code_review.py src/services/stt_engine.py
```

**Script:** `scripts/code_review.py`

```python
"""
Review automático de código con Gemini
"""

import sys
from gemini_init import get_model

REVIEW_PROMPT = """
Eres un code reviewer senior de Python.

Revisa el siguiente código y proporciona:
1. Problemas de seguridad
2. Problemas de performance
3. Violaciones de PEP 8
4. Mejoras sugeridas
5. Calificación (1-10)

CÓDIGO A REVISAR:
```python
{code}
```

FORMATO:
## ⚠️ PROBLEMAS CRÍTICOS
[Lista]

## 💡 SUGERENCIAS
[Lista]

## ⭐ CALIFICACIÓN: X/10
[Justificación]
"""

def review_code(filepath):
    """Hacer review de código"""
    with open(filepath, 'r') as f:
        code = f.read()
    
    model = get_model('arquitecto')
    prompt = REVIEW_PROMPT.format(code=code)
    response = model.generate_content(prompt)
    
    print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python code_review.py [archivo.py]")
        sys.exit(1)
    
    review_code(sys.argv[1])
```

---

## 🔄 WORKFLOW DE DESARROLLO

### Ciclo Típico por Prototipo

```bash
# PASO 1: Leer documento del prototipo
cat docs/04_P1_MOTOR_TRANSCRIPCION.md

# PASO 2: Generar arquitectura
python scripts/gemini_agent.py arquitecto "$(cat docs/04_P1_MOTOR_TRANSCRIPCION.md | grep -A 20 'ARQUITECTURA')"

# PASO 3: Implementar código
python scripts/gemini_agent.py backend "Implementa las clases definidas por el arquitecto"

# PASO 4: Testing manual
python src/services/stt_engine.py

# PASO 5: Si hay error → Debugger
python scripts/gemini_agent.py debugger "$(python src/services/stt_engine.py 2>&1)"

# PASO 6: Review de código
python scripts/code_review.py src/services/stt_engine.py

# PASO 7: Actualizar .md con resultados
# (Manual - tú editas el .md con lo que funcionó)
```

---

## 📝 GESTIÓN DE VERSIONES .md

### Estrategia de Versionado

```
docs/
├── versions/
│   ├── v1.0_12mar2026/         ← Versión inicial (setup)
│   │   ├── 00_PROJECT_MASTER_ACTACLARA.md
│   │   ├── 01_SETUP_ENVIRONMENT.md
│   │   └── ...
│   │
│   ├── v1.1_15mar2026/         ← Post P1 (STT funcionando)
│   │   ├── 04_P1_MOTOR_TRANSCRIPCION.md  (actualizado)
│   │   ├── CHANGELOG.md
│   │   └── ...
│   │
│   └── v1.2_20mar2026/         ← Post P2 (Normalización)
│       └── ...
│
└── [archivos .md actuales]     ← Siempre la última versión
```

### Script de Versionado

**Archivo:** `scripts/version_docs.py`

```python
"""
Crear snapshot de versión de documentación
"""

import os
import shutil
from datetime import datetime

def create_version_snapshot(version_name=None):
    """Crear carpeta con snapshot de docs actuales"""
    
    if not version_name:
        version_name = f"v{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    source = 'docs/'
    dest = f'docs/versions/{version_name}/'
    
    os.makedirs(dest, exist_ok=True)
    
    # Copiar solo .md (no subdirectorios versions)
    for file in os.listdir(source):
        if file.endswith('.md'):
            shutil.copy2(os.path.join(source, file), dest)
    
    # Crear CHANGELOG.md
    changelog = f"""# Cambios en {version_name}

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Modificaciones
- [ ] Listar cambios aquí

## Archivos actualizados
"""
    
    with open(os.path.join(dest, 'CHANGELOG.md'), 'w') as f:
        f.write(changelog)
    
    print(f"✅ Snapshot creado: {dest}")

if __name__ == "__main__":
    import sys
    version = sys.argv[1] if len(sys.argv) > 1 else None
    create_version_snapshot(version)
```

**Uso:**

```bash
# Crear snapshot con nombre automático
python scripts/version_docs.py

# Crear snapshot con nombre específico
python scripts/version_docs.py "v1.1_post_p1"
```

---

## 🎯 MEJORES PRÁCTICAS

### 1. Prompts Claros y Específicos

❌ **Malo:**
```
"Haz el código del transcriptor"
```

✅ **Bueno:**
```
"Implementa la clase TranscripcionLocal que:
- Hereda de MotorTranscripcion (interfaz)
- Usa faster-whisper modelo 'small'
- Método transcribir(audio: ArchivoAudio, idioma: str) -> Transcripcion
- Maneja errores de archivo no encontrado
- Retorna objeto Transcripcion con texto y WER estimado"
```

### 2. Iterar en Pequeños Pasos

```bash
# NO hacer todo de una vez
python scripts/gemini_agent.py backend "Implementa todo P1"  # ❌

# SÍ hacer paso a paso
python scripts/gemini_agent.py backend "Implementa solo método load_audio()"  # ✅
python scripts/gemini_agent.py backend "Implementa solo método transcribe()"  # ✅
python scripts/gemini_agent.py backend "Integra load_audio + transcribe"     # ✅
```

### 3. Siempre Validar Output

```bash
# Después de generar código
python outputs/backend_1234567890.py  # Ejecutar para ver si funciona

# Si falla
python scripts/gemini_agent.py debugger "$(python outputs/backend_1234567890.py 2>&1)"
```

---

## ✅ CHECKLIST DE SETUP

- [ ] `gemini_init.py` creado y funcional
- [ ] API key configurada en `.env`
- [ ] Carpeta `prompts/` con archivos base de cada agente
- [ ] Carpeta `scripts/` con herramientas de CLI
- [ ] Carpeta `outputs/` para guardar código generado
- [ ] Test de conexión exitoso (`python scripts/gemini_init.py`)

---

## 🎯 PRÓXIMO PASO

**→ Leer `03_P0_ARQUITECTURA_BASE.md`**

Con Gemini CLI configurado, estás listo para usar los agentes en el desarrollo de P0.

---

**Versión:** 1.0  
**Estado:** ✅ Listo para uso  
**Agentes configurados:** 4 (Arquitecto, Backend, UI, Debugger)
