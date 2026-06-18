from typing import Optional
from src.database.db import DB
from src.types import User, EstadoUser

class UserManager:
    def __init__(self, phone: str):
        self.db    = DB()
        self.phone = phone

    def get_user(self) -> Optional[User]:

        row = self.db.fetchone("""
            SELECT id, phone, name, estado
            FROM users
            WHERE phone = ?
            LIMIT 1
            """,
            (self.phone,)
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

    def criar_user(self, name: str) -> User:

        self.db.executar_modif("""
            INSERT INTO users (phone, name, estado, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (self.phone, name, "cadastro_prestador")
        )

        print(f"CRIANDO USER NO DB\n")

        user = self.get_user(self.phone)

        if not user:
            raise ValueError("erro ao criar usuario")
        
        return User

    def update_state(self, novo_estado: EstadoUser) -> None:

        query = """
            UPDATE users
            SET estado = ?
            WHERE phone = ?
        """
        self.db.executar_modif(query, (novo_estado, self.phone))