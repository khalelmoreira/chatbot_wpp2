from calendar import c
from datetime import datetime
import sqlite3
from src.database.db import DB

class TokensManager:
    def __init__(self):
        self.db = DB()

    def insert_token(self, token: str, project_id: int, expire_at: datetime) -> None:
        self.db.insert(
            "upload_tokens",
            data={
                "token": token,
                "project_id": project_id,
                "expire_at": expire_at.isoformat(),
                "used": "0"
            }
        )

    def get_token(self, token: str) -> sqlite3.Row | None:
        row = self.db.select(
            "upload_tokens",
            columns="prestador_id, expire_at, used",
            where={"token": token}
        )
        return row[0]
    
    def update_used(self, token: str) -> sqlite3.Row | None:
        row = self.db.fetchone_modif("""
            UPDATE upload_tokens SET
                used = 1
            WHERE token = ?
            AND used = 0
            AND expire_at > datetime('now')
        """, (token,))

        return row