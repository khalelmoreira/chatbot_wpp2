from src.database.db import DB
from src.types import ContextTomador, ContextPrestador, Role, MsgConvType

class MsgManager:
    def __init__(self, ctx: ContextTomador | ContextPrestador):
        self.db  = DB()
        self.ctx = ctx

    def get_msg_history(self, limite: int = 10) -> list[MsgConvType]:

            rows = self.db.fetchall("""
                SELECT
                    role,
                    content
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (self.ctx.conversation_id, limite))
            mensagens = [MsgConvType(**row) for row in rows]
            return list(reversed(mensagens))

    def save_msg(self, role: Role, content: str) -> None:

        self.db.fetchone_modif("""
            INSERT INTO messages (
                prestador_id,
                role,
                content,
                phone
            )
            VALUES (?, ?, ?, ?)
        """, (self.ctx.user.id, role, content, self.ctx.user.phone))