import sqlite3
from typing import Any
from dataclasses import fields
from src.database.db import DB
from src.types import IncomingMessage
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

    def get_db_data(self) -> Prestador | None:
        row = self.db.select_one(
            "prestador",
            columns="razao_social, cnpj, email, regime_tributario, cep",
            where={"id": self.id},
        )
        if not row:
            return None
        return Prestador.from_dict(dict(row))

    def update_valid(self) -> None:

        valid = self.ctx.valid

        data: dict[str, Any] = {
            f.name: getattr(valid, f.name)
            for f in fields(valid)
            if f.name != "address" and getattr(valid, f.name) is not None
        }

        if valid.address is not None:
            data |= {
                f.name: getattr(valid.address, f.name)
                for f in fields(valid.address)
                if getattr(valid.address, f.name) is not None
            }

        if not data:
            return
        
        # SQL explícito: guarded update com RETURNING não suportado pelos helpers genéricos
        set_clause = ", ".join(f"{campo} = ?" for campo in data)
        row = self.db.fetchone_exe(f"""
            UPDATE prestador SET
                {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            AND status = 'COLLECTING'
            RETURNING id
        """, (*data.values(), self.ctx.user.id))

        if row is None:
            raise InvalidTransactionError(f"Nenhuma linha COLETANDO encontrada para id={self.ctx.user.id}")
        
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