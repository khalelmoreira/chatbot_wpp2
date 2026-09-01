from src.database.db import DB
from src.services.ai.history import AIMessage, to_ai_history
from src.types import Role, User


class MsgManager:
    def __init__(self, user: User):
        self.db = DB()
        self.user = user
        self.id = user.id

    def get_msg_history(self, limite: int = 10) -> list[dict[str, str]]:
        # `messages` é indexada por prestador, não por conversa (não há coluna
        # conv_id). Busca as `limite` mais recentes (id DESC) e devolve em ordem
        # cronológica.
        rows = self.db.select(
            "messages",
            columns="role, content",
            where={"prestador_id": self.id},
            order_by="id DESC",
            limit=limite,
        )
        return [dict(row) for row in reversed(rows)]

    def get_ai_history(self, limite: int = 8) -> list[AIMessage]:
        # A mensagem recebida já foi persistida antes do dispatch (initial_handler),
        # então ela é a última linha — descarta para o histórico não repetir o texto
        # que a própria chamada de IA já recebe como user_msg.
        rows = self.get_msg_history(limite + 1)
        return to_ai_history(rows[:-1])

    def save_msg(self, role: Role, content: str) -> None:
        self.db.insert(
            "messages",
            data={
                "prestador_id": self.id,
                "role": role,
                "content": content,
                "phone": self.user.phone,
            },
        )
