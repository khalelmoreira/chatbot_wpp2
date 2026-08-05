from datetime import datetime
from typing import Any
from src.database.db import DB

class TokensManager:
    def __init__(self):
        self.db = DB()

    def insert_token(self, token: str, prestador_id: int, project_id: str, expire_at: datetime) -> None:
        self.db.insert(
            "upload_tokens",
            data={
                "token": token,
                "prestador_id": prestador_id,
                "project_id": project_id,
                "expire_at": expire_at.isoformat(),
                "used": 0
            }
        )

    def get_token(self, token: str) -> dict[str, Any] | None:
        row = self.db.select_one(
            "upload_tokens",
            columns="prestador_id, expire_at, used",
            where={"token": token}
        )
        if row is None:
            return None
        return dict(row)
    
    def update_used(self, token: str) -> dict[str, Any] | None:
        row = self.db.fetchone_exe("""
            UPDATE upload_tokens SET
                used = 1
            WHERE token = ?
            AND used = 0
            AND expire_at > datetime('now')
            RETURNING token
        """, (token,))
        if row is None:
            return None
        return dict(row)