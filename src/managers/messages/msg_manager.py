from src.database.db import DB
from src.types import ContextTomador, Role, MessageType

class MsgManager:
    def __init__(self, ctx: ContextTomador):
        self.db  = DB()
        self.ctx = ctx

    def get_msg_history(self, limite: int = 10) -> list[MessageType]:

            rows = self.db.fetchall("""
                SELECT
                    role,
                    content
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (self.ctx.conversation_id, limite))
            mensagens = [MessageType(**row) for row in rows]
            return list(reversed(mensagens))

    def save_msg(self, role: Role, content: str) -> int:

        row = self.db.fetchone_modif("""
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )
            VALUE (?, ?, ?)
            RETURNING id
        """, (self.ctx.conversation_id, role, content))
        return row["id"]