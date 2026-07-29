from typing import Any
from src.types import ContextTomador
from src.database.db import DB

class OnboardingManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx
        self.id = ctx.user.id

    def resumo_nfs(self) -> dict[str, Any] | None:
        """
        SQL explícito (não usa select() genérico): requer JOIN com conversations
        e ORDER BY + LIMIT para pegar o registro mais recente.
        """

        row = self.db.fetchone("""
            SELECT 
                n.status,
                n.erro_msg,
                n.created_at,
                n.updated_at,
                n.invoice_id
            FROM nfs n
            JOIN conversations c ON
                c.id = n.conv_id
            WHERE c.prestador_id = ?
            ORDER BY n.created_at DESC
            LIMIT 1
        """, (self.id,))
        if row is None:
            return None
        return dict(row)
    
    def get_nf_history(self, limit: int = 5) -> list[dict[str, Any]]:
        rows = self.db.fetchall("""
            SELECT
                id,
                status,
                conv_id,
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
        """, (self.id, limit))
        return [dict(row) for row in rows]
    
    def get_msg_history(self, limit: int = 5) -> list[dict[str, str]]:
        rows = self.db.select(
            "messages",
            columns="role, content",
            where={"prestador_id": self.id},
            order_by="id ASC",
            limit=limit
        )
        return [dict(row) for row in rows]