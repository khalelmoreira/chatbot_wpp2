from config import DB_PATH
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def executar_modif(query: str, params: tuple = ()):

    #INSERT, UPDATE, DELETE. RETORNAR ROWCOUNT.

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount
    
def fetchone(query: str, params: tuple = ()):

    #FETCH ONE

    with get_connection() as conn:
        return conn.execute(query, params).fetchone()

def fetchall(query: str, params: tuple = ()):

    #FETCHALL

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()

def init_db():

    #Salva informacoes do usuario                                  #ESTADO PODE SER MELHOR ENUM!
    executar_modif("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            nome TEXT,
            cpf_cnpj TEXT,
            email TEXT,
            estado TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    #Salva informacoes da mensagem na TABLE mensagens
    executar_modif("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            tipo TEXT,
            mensagem_id TEXT UNIQUE,
            timestamp INTEGER,
            conteudo TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS nf_parcial (
        phone TEXT PRIMARY KEY,
        nf TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP   
        )
    """)

    executar_modif("""
        CREATE TABLE IF NOT EXISTS fila_emissao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT NOT NULL DEFAULT 'pendente',
        payload TEXT NOT NULL,
        tentativas INTEGER DEFAULT 0,
        erro TEXT,
        idempotency_key TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processado_em TIMESTAMP     
        )
    """)