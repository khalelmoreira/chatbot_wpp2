import sqlite3
from typing import Any
from src.types import ContextPrestador, DadosPrestador, Endereco, ProjectPrestador, UserStatus, InvalidTransactionError
from src.database.db import DB

class PrestadorManager:
    def __init__(self, ctx: ContextPrestador):
        self.db  = DB()
        self.ctx = ctx

    def update_validos(self) -> None:
        validos = self.ctx.validation.valid
        
        campos = list(validos.keys())
        set_clause = ", ".join(f"{campo} = ?" for campo in campos)
        valores = [validos[campo] for campo in campos]

        row = self.db.fetchone_modif(f"""
            UPDATE prestador SET
                {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            AND status = 'COLLECTING'
            RETURNING id
        """, (*valores, self.ctx.user.id))

        if row is None:
            raise InvalidTransactionError(f"Nenhuma linha COLETANDO encontrada para id={self.ctx.user.id}")
        
    def update_state(self, novo_status: str) -> None:

        self.db.executar_modif("""
            UPDATE prestador SET
                status = ?
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, self.ctx.user.id))

    def update_error(self, novo_status: str, error_msg: str) -> None:

        self.db.executar_modif("""
            UPDATE prestador SET
                status = ?,
                error_msg = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, error_msg, self.ctx.user.id))

    def get_db_data(self) -> dict[str, Any] | None:

        row = self.db.fetchone("""
            SELECT
                razao_social,
                cnpj,
                email,
                regime_tributario,
                cep
            FROM prestador
            WHERE id = ?
        """, (self.ctx.user.id,))
        if row:
            return dict(row)
        return
    
    def get_all(self) -> dict[str, Any] | None:

        row = self.db.fetchone("""
            SELECT
                razao_social,
                cnpj,
                email,
                regime_tributario,
                cep,
                logradouro,
                numero,
                bairro,
                cidade,
                uf
            FROM prestador
            WHERE id = ?
        """, (self.ctx.user.id,))
        if row:
            return dict(row)
        return
    
    def update_project_id(self, ntaas_project_id: str, novo_status: str) -> None:
        row = self.db.fetchone_modif("""
            UPDATE prestador SET
                ntaas_project_id = ?,
                status = ?
            WHERE id = ?
            AND status = 'CONFIRMING'
            RETURNING id
        """, (ntaas_project_id, novo_status, self.ctx.user.id))
        if not row:
            return
        
    def get_project_id(self) -> sqlite3.Row | None:
        row = self.db.fetchone("""
            SELECT
                ntaas_project_id
            FROM prestador
            WHERE id = ?
            AND status = 'CERTIFICATE'
        """, (self.ctx.user.id))
        return row

    def update_api_key(self, api_key, novo_status: str) -> sqlite3.Row | None:
        row = self.db.fetchone_modif("""
            UPDATE prestador SET
                ntaas_api_key = ?,
                status = ?,
            WHERE id = ?
            AND status = 'CERTIFICATE'
            RETURNING id
        """, (api_key, novo_status, self.ctx.user.id))
        return row