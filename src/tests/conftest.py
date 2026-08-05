import pytest
import src.database.get_connection as get_connection_module
from src.database.tables_db import init_db
from src.database.db import DB


@pytest.fixture
def db(tmp_path, monkeypatch) -> DB:
    """Banco sqlite descartável por teste, isolado do whatsapp.db real."""
    monkeypatch.setattr(get_connection_module, "DB_PATH", tmp_path / "test.db")
    init_db()
    return DB()
