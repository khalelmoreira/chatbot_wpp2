import json
import sqlite3
from typing import Any
from src.types import ContextTomador
from src.database.db import DB
from src.utils.debug import print_table

class ConvManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx
        self.id = ctx.user.id
        self.phone = ctx.user.phone
        self.cid = ctx.conversation_id


    def get_all(self) -> sqlite3.Row:
        row = self.db.select(
            "conversations",
            where={"prestador_id": self.id},
            order_by="created_at DESC",
            limit=1
        )
        return row[0]
    
    def get_status(self) -> str:
        row = self.db.select(
            "conversations",
            columns="status",
            where={"phone": self.phone}
        )
        return row[0]["status"]

    def get_ativa(self) -> sqlite3.Row | None:

        return self.db.fetchone("""
            SELECT * FROM conversations
            WHERE prestador_id = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.ctx.user.id,))
        
    def create_conversation(self) -> int:
        row = self.db.insert(
            "conversations",
            data={
                "phone": self.phone,
                "prestador_id": self.id,
                "status": "COLLECTING",
                "draft_json": "{}",
                "created_at": "datetime('now')"
            },
            returning="id"
        )
        return row["id"]
    
    def update_state(self, novo_status: str) -> None:
        self.db.update(
            "conversations",
            data={"status": novo_status, "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.cid}
        )

    def get_draft(self) -> dict[str, Any]:
        row = self.db.select(
            "conversations",
            columns="draft_json",
            where={"id": self.cid}
        )
        return json.loads(row[0]["draft_json"])

    def update_draft(self, draft: dict) -> None:
        self.db.update(
            "conversations",
            data={"draft_json": json.dumps(draft), "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.cid}
        )
        print_table(table_name="conversations", columns=["draft_json"], where="id = ?", params=(self.ctx.conversation_id,))