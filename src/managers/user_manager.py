from typing import Optional
from src.database.db import fetchone, executar_modif
from src.types.context_base import User
from src.types.estado_user import EstadoUser
from src.types.incoming_msg import IncomingMessage

class UserManager:

    def get_user(self, phone: str) -> Optional[User]:

        row = fetchone("""
            SELECT id, phone, name, estado
            FROM users
            WHERE phone = ?
            LIMIT 1
            """,
            (phone,)
        )
        
        if not row:
            return None
        
        estado = row["estado"] or "novo"

        return User(
            id=row["id"],
            phone=row["phone"],
            name=row["name"],
            estado=estado,
        )

    def criar_user(self, ctx_meta: IncomingMessage) -> User:

        phone = ctx_meta.phone
        name = ctx_meta.name

        executar_modif("""
            INSERT INTO users (phone, name, estado, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (phone, name, "cadastro_prestador")
        )

        print(f"CRIANDO USER NO DB\n")

        user = self.get_user(phone)

        if not user:
            raise ValueError("erro ao criar usuario")
        
        return User

    def update_state(self, phone: str, novo_estado: EstadoUser) -> None:

        query = """
            UPDATE users
            SET estado = ?
            WHERE phone = ?
        """
        executar_modif(query, (novo_estado, phone))