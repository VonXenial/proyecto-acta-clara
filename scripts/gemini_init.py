"""
Inicialización de Gemini CLI para ActaClara
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configurar API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Modelos disponibles en Google Antigravity
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
