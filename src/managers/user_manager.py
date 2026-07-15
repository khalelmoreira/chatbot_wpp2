import sqlite3
from src.database.db import DB
from src.types import IncomingMessage
from typing import Any
from src.types import ContextPrestador, InvalidTransactionError, Prestador, User


class UserManager:
    def __init__(self):
        self.db    = DB()

    def get_user(self, phone: str) -> User | None:
        row = self.db.select_one("prestador", columns="id, phone, status", where={"phone": phone})
        if not row:
            return None
        return User.from_dict(dict(row))

    def criar_user(self, msg: IncomingMessage) -> int:
        return self.db.insert(
            "prestador",
            data={
                "phone": msg.phone,
                "name": msg.name,
                "created_at": "datetime('now')",
                "updated_at": "datetime('now')"
            },
            returning="id"
        )

class PrestadorManager:
    def __init__(self, ctx: ContextPrestador):
        self.db  = DB()
        self.ctx = ctx
        self.id = ctx.user.id

    def update_validos(self) -> None:

        row = self.db.update_guarded(
            "prestador",
            data={""self.ctx.validation.valid},
            where={"id": self.id, "status": "COLLECTING"}
        )

        if row is None:
            raise InvalidTransactionError(f"Nenhuma linha 'COLLECTING' encontrada para id={self.id}")
        
    def update_state(self, novo_status: str) -> None:
        self.db.update(
            "prestador",
            data={"status": novo_status, "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.id}
        )

    def update_error(self, novo_status: str, error_msg: str) -> None:
        self.db.update(
            "prestador",
            data={"status": novo_status, "error_msg": error_msg, "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.id}
        )

    def get_db_data(self) -> dict[str, Any] | None:
        row = self.db.select(
            "prestador",
            columns="razao_social, cnpj, email, regime_tributario, cep",
            where={"id": self.id},
            limit=1
        )
        if row:
            return dict(row[0])
        return
    
    def get_all(self) -> list[Prestador]:
        rows = self.db.select(
            "prestador",
            columns=(
                "razao_social,"
                "cnpj,"
                "email,"
                "regime_tributario,"
                "cep,"
                "logradouro,"
                "numero,"
                "bairro,"
                "cidade,"
                "uf"
            ),
            where={"id": self.id}
        )
        return [Prestador.from_dict(dict(row)) for row in rows]
    
    def update_project_id(self, ntaas_project_id: str, novo_status: str) -> None:
        row = self.db.update_guarded(
            "prestador",
            data={"ntaas_project_id": ntaas_project_id, "status": novo_status},
            where={"id": self.id, "status": "CONFIRMING"}
        )
        if not row:
            return
        
    def get_project_id(self) -> list[sqlite3.Row]:
        return self.db.select(
            "prestador",
            columns="ntaas_project_id",
            where={"id": self.id, "status": 'CERTIFICATE'}
        )

    def update_api_key(self, api_key, novo_status: str) -> sqlite3.Row | None:
        row = self.db.update_guarded(
            "prestador",
            data={"ntaas_api_key": api_key, "status": novo_status},
            where={"id": self.id, "status": "CERTIFICATE"}
        )
        return row