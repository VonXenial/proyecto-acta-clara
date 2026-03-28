"""
Punto de entrada oficial de ActaClara v1.0.
"""

import sys
import os
import ctypes

# Identificador exclusivo para que Windows agrupe las ventanas y muestre el logo en la barra de tareas
try:
    myappid = 'vonxenial.actaclara.desktop.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Suprimir advertencia de symlinks de HuggingFace en Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Añadir la raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Añadir carpeta bin al PATH del sistema para FFmpeg
bin_path = os.path.join(project_root, "bin")
if os.path.exists(bin_path):
    os.environ["PATH"] = bin_path + os.pathsep + os.environ["PATH"]

from src.ui.main_window import MainWindow  # noqa: E402 # type: ignore

def main():
    """Lanza la aplicación principal."""
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
