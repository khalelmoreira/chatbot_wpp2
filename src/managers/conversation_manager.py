import json
import sqlite3
from typing import Optional
from src.types.context_tomador import ContextTomador
from src.database.db import executar_modif, fetchone

class ConversationManager:

    def get_status(self, phone: str):

        row = fetchone("""
            SELECT status FROM conversations
            WHERE phone = ?
            LIMIT 1
        """, (phone,))

        return row["status"]

    def get_ativa(self, prestador_id: int) -> Optional[sqlite3.Row]:
        # Retorna a conversa ativa do número, ou None se estiver em IDLE

        return fetchone("""
            SELECT * FROM conversations
            WHERE prestador_id = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (prestador_id,))
        
    def create_conversation(self, ctx: ContextTomador) -> int:

        row = fetchone("""
            INSERT INTO conversations (phone, prestador_id, status, draft_json, created_at)
            VALUES (?, ?, 'COLLECTING', '{}', datetime('now'))
            RETURNING id
        """, (ctx.user.phone, ctx.user.id))

        return row["id"]
    
    def update_state(self, conversation_id: int, status: str) -> None:

        executar_modif("""
            UPDATE conversations
            SET status = ?,
            updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, conversation_id))

    def get_draft(self, ctx: ContextTomador) -> None:

        row = fetchone("""
            SELECT draft_json FROM conversations
            WHERE id = ?
        """, (ctx.conversation_id,))

        return json.loads(row["draft_json"])

    def update_draft(self, conversation_id: int, draft: dict) -> None:

        executar_modif("""
            UPDATE conversations
            SET draft_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(draft), conversation_id))