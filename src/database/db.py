from src.database.get_connection import get_connection

class DB:
    def executar_modif(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
        
    def fetchone(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            return conn.execute(query, params).fetchall()
        
    def fetchone_modif(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()