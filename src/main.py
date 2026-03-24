"""
Punto de entrada oficial de ActaClara v1.0.
"""

import sys
import os

# Añadir la raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow

def main():
    """Lanza la aplicación principal."""
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
