"""
CLI para ejecutar agentes Gemini
"""

import sys
import os
import time
from gemini_init import get_model

def run_agent(agent_name, task_description):
    """Ejecutar agente con tarea específica"""
    
    # Rutas de prompts
    prompt_file = f"prompts/{agent_name}_base.txt"
    
    if not os.path.exists(prompt_file):
        print(f"❌ No se encontró el prompt base: {prompt_file}")
        return

    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_base = f.read()
    
    prompt_completo = f"{prompt_base}\n\nTAREA ESPECÍFICA:\n{task_description}"
    
    model = get_model(agent_name)
    response = model.generate_content(prompt_completo)
    
    print(f"\n{'='*60}")
    print(f"AGENTE: {agent_name.upper()}")
    print(f"{'='*60}\n")
    print(response.text)
    
    # Guardar resultado
    os.makedirs("outputs", exist_ok=True)
    output_file = f"outputs/{agent_name}_{int(time.time())}.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"\n✅ Guardado en: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python gemini_agent.py [agente] [tarea]")
        print("Agentes: arquitecto, backend, ui, debugger")
        sys.exit(1)
    
    run_agent(sys.argv[1], sys.argv[2])
