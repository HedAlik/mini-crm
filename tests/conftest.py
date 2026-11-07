import sys
from pathlib import Path

# Permite `import app` al ejecutar pytest desde la raíz del proyecto.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
