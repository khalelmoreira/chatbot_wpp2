import json
import sqlite3
from typing import Optional
from src.database.db import executar_modif, fetchall, fetchone, get_connection

class ConversationManager:

    def get_active_conversation(self, phone: str) -> Optional[sqlite3.Row]:
        # Retorna a conversa ativa do número, ou None se estiver em IDLE

        return fetchone("""
            SELECT * FROM conversations
            WHERE phone = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (phone,))
        
    def create_conversation(self, phone: str) -> int:

        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations (phone, status)
                VALUE (?, 'COLLECTING')
                RETURN id
            """, (phone,))

            conversation_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO nfse_drafts (conversation_id, dados)
                VALUES (?, '{}')
            """, (conversation_id,))

        return conversation_id
    
    def update_status(self, conversation_id: int, status: int) -> None:

        executar_modif("""
            UPDATE conversations
            SET status = ?,
            updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, conversation_id))

    def add_message(self, conversation_id: int, role: str, content: str) -> None:

        executar_modif("""
            INSERT INTO messages (conversation_id, role, content)
            VALUE (?, ?, ?)
        """, (conversation_id, role, content))

    def get_history(self, conversation_id: int) -> list[dict]:

        rows = fetchall("""
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        return [{"role": row["role"], "content": row["content"]} for row in rows]
    
    def get_draft(self, conversation_id: int) -> dict:

        row = fetchone("""
            SELECT dados FROM nfse_drafts
            WHERE conversation_id = ?
        """, (conversation_id,))

        return json.loads(row["dados"]) if row else {}
    
    def update_draft(self, conversation_id: int, dados: dict) -> None:

        executar_modif("""
            UPDATE nfse_draft
            SET dados = ?, updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
        """, (json.dumps(dados), conversation_id))

    def save_nfse_emitida(
            self,
            conversation_id: int,
            numero_nota: Optional[str],
            protocolo: Optional[str],
            dados_enviados: dict,
            resposta_api: dict,
    ) -> None:
        
        executar_modif("""
            INSERT INTO nfse_emitidas
                (conversation_id, numero_nota, protocolo, dados_enviados, resposta_api)
            VALUE (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            numero_nota,
            protocolo,
            json.dumps(dados_enviados),
            json.dumps(resposta_api),
        ))