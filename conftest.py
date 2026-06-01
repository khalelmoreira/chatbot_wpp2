import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
