from dataclasses import fields
from typing import Any

from src.database.db import DB
from src.types import (
    Address,
    ContextPrestador,
    IncomingMessage,
    InvalidTransactionError,
    Prestador,
    User,
    UserStatus,
)


class UserManager:
    def __init__(self):
        self.db    = DB()

    def get_user(self, phone: str) -> User | None:
        row = self.db.select_one("prestador", columns="id, phone, status, channel", where={"phone": phone})
        if not row:
            return None
        return User.from_dict(dict(row))

    def criar_user(self, msg: IncomingMessage) -> int:
        return self.db.insert(
            "prestador",
            data={
                "phone": msg.phone,
                "name": msg.name,
                "channel": msg.channel,
            },
            returning="id"
        )

class PrestadorManager:
    def __init__(self, ctx: ContextPrestador | None = None):
        self.db  = DB()
        self.ctx = ctx
        self.id  = ctx.user.id if ctx is not None else None

    @classmethod
    def for_id(cls, prestador_id: int) -> "PrestadorManager":
        """Constrói o manager fora do fluxo conversacional (ex.: handler HTTP do upload de
        certificado), onde não existe ContextPrestador."""
        manager = cls()
        manager.id = prestador_id
        return manager

    def get_db_data(self) -> Prestador | None:
        row = self.db.select_one(
            "prestador",
            columns=(
                "razao_social, cnpj, email, regime_tributario, cep, "
                "address_logradouro AS logradouro, address_numero AS numero, "
                "address_complemento AS complemento, address_bairro AS bairro, "
                "address_cidade AS cidade, address_uf AS uf"
            ),
            where={"id": self.id},
        )
        if not row:
            return None

        data = dict(row)
        data["id"] = self.id
        data["phone"] = self.ctx.user.phone
        return Prestador.from_dict(dict(data))

    def update_valid(self) -> None:

        valid = self.ctx.valid

        data: dict[str, Any] = {
            f.name: getattr(valid, f.name)
            for f in fields(valid)
            if f.name != "address" and getattr(valid, f.name) is not None
        }

        if valid.address is not None:
            data |= {
                f"address_{f.name}": getattr(valid.address, f.name)
                for f in fields(valid.address)
                if getattr(valid.address, f.name) is not None
            }

        if not data:
            return
        
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
            data={"status": novo_status},
            where={"id": self.id}
        )

    def enter_help(self, return_to: str | None) -> None:
        """Guarda o UserStatus atual em help_return_to e move para HELP. `return_to`
        None significa que o usuário veio do idle (sem cadastro)."""
        self.db.update(
            "prestador",
            data={"status": UserStatus.HELP, "help_return_to": return_to},
            where={"id": self.id},
        )

    def leave_help(self) -> str | None:
        """Restaura o status guardado em help_return_to (None volta ao idle) e limpa
        a coluna. Devolve o status restaurado."""
        row = self.db.select_one("prestador", columns="help_return_to", where={"id": self.id})
        return_to = row["help_return_to"] if row else None
        self.db.update(
            "prestador",
            data={"status": return_to, "help_return_to": None},
            where={"id": self.id},
        )
        return return_to

    def update_error(self, novo_status: str, error_msg: str) -> None:
        self.db.update(
            "prestador",
            data={"status": novo_status, "error_msg": error_msg},
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

    def get_address(self) -> Address | None:
        row = self.db.select_one(
            "prestador",
            columns=(
                "address_logradouro AS logradouro,"
                "address_numero AS numero,"
                "address_complemento AS complemento,"
                "address_bairro AS bairro,"
                "address_cidade AS cidade,"
                "address_uf AS uf"
            ),
            where={"id": self.id},
        )
        if not row:
            return None
        return Address.from_dict(dict(row))

    def update_address(self) -> None:
        address = self.ctx.valid

        data: dict[str, Any] = {
            f"address_{f.name}": getattr(address, f.name)
            for f in fields(address)
            if getattr(address, f.name) is not None
        }
        if not data:
            return

        set_clause = ", ".join(f"{campo} = ?" for campo in data)
        row = self.db.fetchone_exe(f"""
            UPDATE prestador SET
                {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            AND status = 'ADDRESS'
            RETURNING id
        """, (*data.values(), self.id))

        if row is None:
            raise InvalidTransactionError(f"Nenhuma linha COLETANDO encontrada para id={self.id}")
        
    def update_project_id(self, ntaas_project_id: str, novo_status: str) -> None:
        row = self.db.update_guarded(
            "prestador",
            data={"ntaas_project_id": ntaas_project_id, "status": novo_status},
            where={"id": self.id, "status": "PROJECT"}
        )
        if row is None:
            raise InvalidTransactionError(f"Prestador id={self.id} não estava em PROJECT ao persistir ntaas_project_id")

    def get_project_id(self) -> str | None:
        row = self.db.select_one(
            "prestador",
            columns="ntaas_project_id",
            where={"id": self.id, "status": "CERTIFICATE"}
        )
        return row["ntaas_project_id"] if row else None

    def update_api_key(self, api_key, novo_status: str) -> dict[str, Any] | None:
        row = self.db.update_guarded(
            "prestador",
            data={"ntaas_api_key": api_key, "status": novo_status, "certificado_enviado": 1},
            where={"id": self.id, "status": "CERTIFICATE"},
            returning="id, phone, channel",
        )
        if row is None:
            return None
        return dict(row)