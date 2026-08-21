from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "whatsapp.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
MAX_TENTATIVAS = 3