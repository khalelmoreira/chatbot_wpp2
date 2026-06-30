import json
import sqlite3
from typing import Optional, Any
from src.types import ContextTomador
from src.database.db import DB
from src.utils.debug import print_table

class ConversationManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx

    def get_all(self) -> sqlite3.Row:

        return self.db.fetchone("""
            SELECT
                *
            FROM conversations
            WHERE prestador_id = ?
            ORDER BY created_at DESC
            LIMIT 1;
        """, (self.ctx.user.id,))

    def get_status(self):

        row = self.db.fetchone("""
            SELECT status FROM conversations
            WHERE phone = ?
            LIMIT 1
        """, (self.ctx.user.phone,))

        return row["status"]

    def get_ativa(self) -> Optional[sqlite3.Row]:

        return self.db.fetchone("""
            SELECT * FROM conversations
            WHERE prestador_id = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.ctx.user.id,))
        
    def create_conversation(self) -> int:

        row = self.db.fetchone("""
            INSERT INTO conversations (
                phone,
                prestador_id,
                status,
                draft_json,
                created_at
            )
            VALUES (?, ?, 'COLLECTING', '{}', datetime('now'))
            RETURNING id
        """, (self.ctx.user.phone, self.ctx.user.id))

        return row["id"]
    
    def update_state(self, novo_status: str) -> None:

        self.db.executar_modif("""
            UPDATE conversations SET
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, self.ctx.conversation_id))

    def get_draft(self) -> dict[str, Any]:

        row = self.db.fetchone("""
            SELECT
                draft_json
            FROM conversations
            WHERE id = ?
        """, (self.ctx.conversation_id,))

        return json.loads(row["draft_json"])

    def update_draft(self, draft: dict) -> None:

        self.db.executar_modif("""
            UPDATE conversations SET
                draft_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(draft), self.ctx.conversation_id))

        print_table(table_name="conversations", columns=["draft_json"], where="id = ?", params=(self.ctx.conversation_id,))