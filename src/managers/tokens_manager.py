from calendar import c
from datetime import datetime
from typing import Any
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

    def get_token(self, token: str) -> dict[str, Any] | None:
        row = self.db.select(
            "upload_tokens",
            columns="prestador_id, expire_at, used",
            where={"token": token}
        )
        if row is None:
            return None
        return dict(row[0])
    
    def update_used(self, token: str) -> dict[str, Any] | None:
        row = self.db.fetchone_exe("""
            UPDATE upload_tokens SET
                used = 1
            WHERE token = ?
            AND used = 0
            AND expire_at > datetime('now')
        """, (token,))
        if row is None:
            return None
        return dict(row)