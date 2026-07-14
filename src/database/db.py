import sqlite3
from typing import Any
from src.database.get_connection import get_connection

class DB:
    def _exe_modif(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
        
    def _fetchone(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def _fetchall(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            return conn.execute(query, params).fetchall()
        
    def _fetchone_modif(self, query: str, params: tuple = ()):

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        
    def select(self, table: str, columns: str = "*",
               where: dict[str, object] | None = None, order_by: str | None = None,
               limit: int | None = None) -> list[sqlite3.Row]:
        
        """
        SELECT genérico com filtro AND-only, ordenação e limite opcionais.
        Usado para listagens e buscas que podem retornar múltiplas linhas.
        Retorna lista vazia se nada satisfez o WHERE.
        """
        
        query = f"SELECT {columns} FROM {table}"
        params: tuple = ()

        if where:
            clauses = [f"{k} = ?" for k in where]
            query += f" WHERE " + " AND ".join(clauses)
            params = tuple(where.values())

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        return self._fetchall(query, params)
    
    def select_one(self, table: str, where: dict[str, object], columns: str = "*"):

        """
        Atalho para select() quando se espera no máximo uma linha (ex.: busca por chave única).
        Retorna None se nenhuma linha satisfez o WHERE, em vez de lista vazia.
        """

        rows = self.select(table, columns, where, limit=1)
        return rows[0] if rows else None
    
    def insert(self, table: str, data: dict[str, object], returning: str | None = None) -> Any:

        """
        INSERT genérico. Sem `returning`, retorna o lastrowid (int) da linha inserida.
        Com `returning`, retorna o valor da coluna pedida via RETURNING — útil quando
        o id gerado não é o lastrowid (ex.: chave não-autoincrement) ou quando se
        quer outro campo gerado pelo banco (ex.: default de timestamp).
        """

        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"""
            INSERT INTO {table} ({cols})
            VALUES ({placeholders})
            """

        if returning:
            query += f" RETURNING {returning}"
            row = self._fetchone_modif(query, tuple(data.values()))
            return row[returning]
        
        return self._exe_modif(query, tuple(data.values()))
    
    def update(self, table: str, data: dict[str, object], where: dict[str, object]) -> int:

        """
        UPDATE incondicional. Não verifica estado anterior nem retorna a linha afetada.
        Usado quando não há necessidade de confirmar transição de estado (ex.: atualizar
        um campo de cadastro que não depende do valor atual).
        """

        set_clause = ", ".join(f"{k} = ?" for k in data)
        where_clause = " AND ".join(f"{k} = ?" for k in where)

        query = f"""
            UPDATE {table} SET
                {set_clause}
            WHERE {where_clause}
            """
        return self._exe_modif(query, tuple(data.values()) + tuple(where.values()))
    
    def update_guarded(self, table: str, data: dict[str, object],
                       where: dict[str, object], returning: str = "id") -> sqlite3.Row | None:
        
        """
        UPDATE com guarda de estado + RETURNING.
        Usado para transições condicionais (ex.: só atualiza se status atual bate).
        Retorna None se nenhuma linha satisfez o WHERE (guarda falhou).
        """

        set_clause = ", ".join(f"{k} = ?" for k in data)
        where_clause = " AND ".join(f"{k} = ?" for k in where)

        query = f"""
            UPDATE {table} SET
                {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE {where_clause}
            RETURNING {returning}
        """

        params = tuple(data.values()) + tuple(where.values())
        return self._fetchone_modif(query, params)