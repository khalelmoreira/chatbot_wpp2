from src.database.db import DB
from src.types import ContextPrestador, ContextTomador, Role


class MsgManager:
    def __init__(self, ctx: ContextTomador | ContextPrestador):
        self.db  = DB()
        self.ctx = ctx
        self.id = ctx.user.id

    def get_msg_history(self, limite: int = 10) -> list[dict[str, str]]:
        # `messages` é indexada por prestador, não por conversa (não há coluna
        # conv_id). Mesmo padrão de OnboardingManager.get_msg_history.
        rows = self.db.select(
            "messages",
            columns="role, content",
            where={"prestador_id": self.id},
            order_by="id ASC",
            limit=limite
        )
        return [dict(row) for row in rows]

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