from src.database.db import DB
from src.types import ContextTomador

class MsgManager:
    def __init__(self, ctx: ContextTomador):
        self.db  = DB()
        self.ctx = ctx

    def get_msg_history(self) -> list[dict]:

            rows = self.db.fetchall("""
                SELECT role, content
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """, (self.ctx.conversation_id,))

            return [{"role": row["role"], "content": row["content"]} for row in rows]

    def add_message(self, role: str, content: str) -> None:

        self.db.executar_modif("""
            INSERT INTO messages (conversation_id, role, content)
            VALUE (?, ?, ?)
        """, (self.ctx.conversation_id, role, content))