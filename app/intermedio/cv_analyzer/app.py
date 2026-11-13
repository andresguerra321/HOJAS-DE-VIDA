import sys
from pathlib import Path

# Asegurar que el directorio de cv_analyzer y el directorio raíz estén en sys.path
CARPETA_CV_ANALYZER = Path(__file__).resolve().parent
if str(CARPETA_CV_ANALYZER) not in sys.path:
    sys.path.insert(0, str(CARPETA_CV_ANALYZER))

CARPETA_RAIZ = CARPETA_CV_ANALYZER.parent.parent.parent
if str(CARPETA_RAIZ) not in sys.path:
    sys.path.append(str(CARPETA_RAIZ))

from ui.streamlit_ui import main

if __name__ == "__main__":
    main()

