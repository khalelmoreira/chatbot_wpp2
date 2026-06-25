import sqlite3
from src.types import ContextTomador
from src.database.db import DB

class OnboardingManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx

    def resumo_nfs(self) -> sqlite3.Row:

        return self.db.fetchone("""
            SELECT 
                n.status,
                n.erro_msg,
                n.created_at,
                n.updated,
                n.invoice_id
            FROM nfs n
            JOIN conversations c ON
                c.id = n.conversation_id
            WHERE c.prestador id = ?
            ORDER BY n.created_at DESC
            LIMIT 1
        """, (self.ctx.user.id))
    