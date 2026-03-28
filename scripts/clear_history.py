import sys
import os

# Ajustar path para importar src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from src.database.db_manager import DBManager # type: ignore

def main():
    db = DBManager()
    confirm = input("¿Estás seguro de que deseas eliminar TODO el historial de la base de datos? (s/n): ")
    if confirm.lower() == 's':
        try:
            db.clear_history()
            print("✅ Historial eliminado correctamente.")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Operación cancelada.")

if __name__ == "__main__":
    main()
