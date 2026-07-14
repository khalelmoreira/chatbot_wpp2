import sqlite3
from src.types import ContextTomador
from src.database.db import DB

class OnboardingManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx
        self.id = ctx.user.id

    def resumo_nfs(self) -> sqlite3.Row:

        """
        SQL explícito (não usa select() genérico): requer JOIN com conversations
        e ORDER BY + LIMIT para pegar o registro mais recente.
        """

        return self.db.fetchone("""
            SELECT 
                n.status,
                n.erro_msg,
                n.created_at,
                n.updated_at,
                n.invoice_id
            FROM nfs n
            JOIN conversations c ON
                c.id = n.conversation_id
            WHERE c.prestador_id = ?
            ORDER BY n.created_at DESC
            LIMIT 1
        """, (self.ctx.user.id,))
    
    def get_nf_history(self, limit: int = 5) -> list[sqlite3.Row]:
        return self.db.fetchall("""
            SELECT
                id,
                status,
                conversation_id,
                tentativas,
                nome,
                cnpj,
                descricao_servico,
                valor_total,
                requested_at,
                created_at,
                invoice_id,
                emitido_em,
                issued_at,
                erro_code,
                erro_msg,
                cancelled_at
            FROM nfs
            WHERE prestador_id = ?
                AND status IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at ASC
            LIMIT ?
        """, (self.ctx.user.id, limit))
    
    def get_msg_history(self, limit: int = 5) -> list[sqlite3.Row]:
        return self.db.select(
            "messages",
            columns="role, content",
            where={"prestador_id": self.id},
            order_by="id ASC",
            limit=limit
        )