import sqlite3
from typing import Any
from src.types import ContextPrestador, DadosPrestador, Endereco, ProjectPrestador, UserStatus, InvalidTransactionError
from src.database.db import DB

class PrestadorManager:
    def __init__(self, ctx: ContextPrestador):
        self.db  = DB()
        self.ctx = ctx

    def update_validos(self) -> None:
        validos = self.ctx.validacao.validos
        
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
        return None
    
    def update_endereco(self, endereco: Endereco) -> None:

        query = """
            INSERT INTO prestador (phone, logradouro, numero, complemento, bairro, cidade, uf, cep)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET
                logradouro  = excluded.logradouro,
                numero      = excluded.numero,
                complemento = excluded.complemento,
                bairro      = excluded.bairro,
                cidade      = excluded.cidade,
                uf          = excluded.uf,
                cep         = excluded.cep,
                updated_at  = CURRENT_TIMESTAMP
        """

        self.db.executar_modif(query, (
        self.ctx.user.phone,
        endereco.logradouro,
        endereco.numero,
        endereco.complemento,
        endereco.bairro,
        endereco.cidade,
        endereco.uf,
        endereco.cep,
    ))
        
    def get_all(self) -> ProjectPrestador:

        query = """
            SELECT
                cnpj,
                razao_social,
                inscricao_municipal,
                regime_tributario,
                email,
                cep,
                logradouro,
                numero,
                bairro,
                cidade,
                uf
            FROM prestador
            WHERE phone = ?
        """
        row = self.db.fetchone(query, (self.ctx.user.phone,))

        if not row:
            return

        return ProjectPrestador(
            name=row["razao_social"],
            cnpj=row["cnpj"],
            razaoSocial=row["razao_social"],
            inscricaoMunicipal=row["inscricao_municipal"],
            regimeTributario=row["regime_tributario"],
            email=row["email"],
            endereco=Endereco(
                logradouro=row["logradouro"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                numero=row["numero"],
            )
        )