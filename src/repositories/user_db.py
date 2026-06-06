from typing import Optional
from src.database.db import fetchone, executar_modif
from src.types.context_base import User, EstadoUser

class UserManager:

    def get_user(self, phone: str) -> Optional[User]:

        row = fetchone(
            """
            SELECT id, phone, estado
            FROM users
            WHERE phone = ?
            LIMIT 1
            """,
            (phone,)
        )

        print(f"VERIFICA ESTADO USER [ROW]: {row}\n")

        if not row:
            return None
        
        estado = row["estado"] or "novo"

        return User(
            id=row["id"],
            phone=row["phone"],
            estado=estado
        )

    def criar_user(self, phone: str) -> User:

        executar_modif(
            """
            INSERT INTO users (phone, estado, created_at)
            VALUES (?, ?, datetime('now'))
            """,
            (phone, "cadastro_prestador")
        )

        print(f"CRIANDO USER NO DB\n")

        user = self.get_user(phone)

        if not user:
            raise ValueError("erro ao criar usuario")
        
        return User

    def update_status(self, user: User, novo_estado: EstadoUser) -> None:

        query = """
            UPDATE users
            SET estado = ?
            WHERE phone = ?
        """
        executar_modif(query, (novo_estado, user.phone))