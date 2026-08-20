import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    # concorrência real (dois telefones diferentes escrevendo ao mesmo tempo,
    # ex.: um webhook do WhatsApp e o EmissaoWorker) faz o SQLite lançar
    # "database is locked" em vez de esperar — busy_timeout faz o driver
    # reter e reter tentar por até 5s antes de propagar o erro.
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()