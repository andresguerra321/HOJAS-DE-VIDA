"""
Lanzador principal desde la raíz del proyecto.
Permite iniciar la aplicación directamente ejecutando:
    streamlit run run_app.py
o bien:
    python run_app.py
"""
import sys
import subprocess
from pathlib import Path

DIRECTORIO_RAIZ = Path(__file__).resolve().parent
DIRECTORIO_CV_ANALYZER = DIRECTORIO_RAIZ / "app" / "intermedio" / "cv_analyzer"

if str(DIRECTORIO_CV_ANALYZER) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_CV_ANALYZER))
if str(DIRECTORIO_RAIZ) not in sys.path:
    sys.path.append(str(DIRECTORIO_RAIZ))

from ui.streamlit_ui import main

if __name__ == "__main__":
    # Si se ejecuta directamente con `python run_app.py`, invocar Streamlit mediante subproceso
    if not any("streamlit" in arg.lower() for arg in sys.argv):
        print("Iniciando Streamlit para Analizador de Currículums con IA...")
        ruta_app = str(DIRECTORIO_CV_ANALYZER / "app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", ruta_app, "--server.port=8501"])
    else:
        main()

