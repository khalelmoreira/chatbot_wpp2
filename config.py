from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "src" / "database" / "whatsapp.db"
MAX_TENTATIVAS = 3