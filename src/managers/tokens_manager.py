from datetime import datetime
import sqlite3
from src.database.db import DB

class TokensManager:
    def __init__(self):
        self.db = DB()

    def insert_token(self, token: str, project_id: int, expire_at: datetime) -> None:
        self.db.executar_modif("""
            INSERT INTO upload_tokens (
                token,
                project_id,
                expire_at,
                used
            )
            VALUES (?, ?, ?, 0)
        """, (token, project_id, expire_at.isoformat()))

    def get_token(self, token: str) -> sqlite3.Row | None:

        row = self.db.fetchone("""
            SELECT
                prestador_id,
                expire_at,
                used
            FROM upload_tokens
            WHERE token = ?
        """, (token,))
        return row
    
    def update_used(self, token: str) -> sqlite3.Row | None:

        row = self.db.fetchone_modif("""
            UPDATE upload_tokens SET
                used = 1
            WHERE token = ?
            AND used = 0
            AND expire_at > datetime('now')
        """, (token,))

        return row