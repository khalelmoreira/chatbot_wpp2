from src.database.get_connection import get_connection

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
    
def fetchone_modif(query: str, params: tuple = ()):

    with get_connection() as conn:
        cursor = conn.cursor()
        print(repr(query))
        cursor.execute(query, params)
        return cursor.fetchone()