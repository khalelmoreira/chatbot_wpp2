from src.database.db import DB
from src.types import ContextPrestador, ContextTomador, MsgConvType, Role


class MsgManager:
    def __init__(self, ctx: ContextTomador | ContextPrestador):
        self.db  = DB()
        self.ctx = ctx
        self.id = ctx.user.id

    @property
    def cid(self) -> int | None:
        """Lido de ctx.conv_id a cada acesso — mesmo motivo do ConvManager.cid:
        um MsgManager pode ser construído antes de ctx.conv_id ser atribuído
        (ex.: IntentService o cria no __init__, antes de criar a conversa)."""
        return self.ctx.conv_id

    def get_msg_history(self, limite: int = 10) -> list[MsgConvType]:
        rows = self.db.select(
            "messages",
            columns="role, content",
            where={"conv_id": self.cid},
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