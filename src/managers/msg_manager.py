from src.database.db import DB
from src.types import ContextTomador, ContextPrestador, Role, MsgConvType

class MsgManager:
    def __init__(self, ctx: ContextTomador | ContextPrestador):
        self.db  = DB()
        self.ctx = ctx
        self.id = ctx.user.id
        self.cid = ctx.conversation_id

    def get_msg_history(self, limite: int = 10) -> list[MsgConvType]:
        rows = self.db.select(
            "messages",
            columns="role, content",
            where={"conversation_id": self.cid},
            order_by="id ASC",
            limit=limite
        )
        mensagens = [MsgConvType(**row) for row in rows]
        return list(mensagens)

    def save_msg(self, role: Role, content: str) -> None:
        self.db.insert(
            "messages",
            data={
                "prestador_id": self.id,
                "role": role,
                "content": content,
                "phone": self.ctx.user.phone
            }
        )