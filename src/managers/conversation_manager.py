import json
import sqlite3
from typing import Optional
from src.types.context_tomador import DadosTomador, Tomador, Servico, Valores, ContextTomador
from src.database.db import executar_modif, fetchall, fetchone, get_connection

class ConversationManager:

    def get_status(self, phone: str):

        return fetchone("""
            SELECT status FROM conversations
            WHERE phone = ?
            LIMIT 1
        """, (phone,))

    def get_active_conversation(self, phone: str) -> Optional[sqlite3.Row]:
        # Retorna a conversa ativa do número, ou None se estiver em IDLE

        return fetchone("""
            SELECT * FROM conversations
            WHERE phone = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (phone,))
        
    def create_conversation(self, ctx: ContextTomador) -> int:

        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations (phone, prestador_id, status, draft_json, created_at)
                VALUES (?, ?, 'COLLECTING', '{}', datetime('now'))
                RETURNING id
            """, (ctx.user.phone, ctx.user.id))

            conversation_id = cursor.lastrowid
  
        return conversation_id
    
    def update_state(self, conversation_id: int, status: str) -> None:

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
    
    def get_draft(self, conversation_id: int, ctx: ContextTomador) -> None:

        row = fetchone("""
            SELECT draft_json FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))

        data = json.loads(row["draft_json"])

        print(f"nfse_drafts.loads: {data}\n")

        nome = data.get("tomador", {}).get("nome")
        cnpj = data.get("tomador", {}).get("cnpj")

        descricao = data.get("servico", {}).get("descricao")
        total = data.get("valores", {}).get("total")
        aliquotaIss = data.get("valores", {}).get("aliquotaIss")

        ctx.dados_db = DadosTomador(
            tomador=Tomador(
                nome=nome,
                cnpj=cnpj
            ),
            servico=Servico(
                descricao=descricao
            ),
            valores=Valores(
                total=total,
                aliquotaIss=aliquotaIss
            )
        )
    
    def update_draft(self, conversation_id: int, draft: dict) -> None:

        executar_modif("""
            UPDATE conversations
            SET draft_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(draft), conversation_id))

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