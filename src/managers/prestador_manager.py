from src.types.context_prestador import ContextPrestador, DadosPrestador, Endereco, ProjectPrestador
from src.database.db import executar_modif, fetchone, fetchall

class PrestadorManager:

    CAMPOS_EDITAVEIS = [
        "razao_social",
        "cnpj",
        "email",
        "regime_tributario",
        "cep",
        "inscricao_municipal",
    ]

    def update_validos(self, ctx: ContextPrestador) -> None:

        phone = ctx.user.phone
        validos = ctx.validacao.validos
        
        campos_insert = ["phone"] + [c for c in validos if c in self.CAMPOS_EDITAVEIS]
        valores_insert = [phone] + [validos[c] for c in campos_insert[1:]]

        placeholders = ", ".join("?" * len(campos_insert))

        campos_update = campos_insert[1:]
        set_clause = ", ".join(f"{c} = excluded.{c}" for c in campos_update)

        query = f"""
            INSERT INTO prestador ({', '.join(campos_insert)})
            VALUES ({placeholders})
            ON CONFLICT(phone) DO UPDATE SET {set_clause}
        """

        executar_modif(query, tuple(valores_insert))

    def get_db_data(self, ctx: ContextPrestador) -> None:

        phone = ctx.user.phone

        query = """
            SELECT
                razao_social,
                cnpj,
                email,
                regime_tributario,
                cep,
                inscricao_municipal
            FROM prestador
            WHERE phone = ?
        """
        row = fetchone(query, (phone,))

        if not row:
            
            ctx.dados_db = DadosPrestador()

            return

        ctx.dados_db = DadosPrestador(
            razao_social=row["razao_social"],
            cnpj=row["cnpj"],
            email=row["email"],
            regime_tributario=row["regime_tributario"],
            cep=row["cep"],
            inscricao_municipal=row["inscricao_municipal"],
        )

    def update_endereco(self, phone: str, endereco: Endereco) -> None:

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

        executar_modif(query, (
        phone,
        endereco.logradouro,
        endereco.numero,
        endereco.complemento,
        endereco.bairro,
        endereco.cidade,
        endereco.uf,
        endereco.cep,
    ))
        
    def get_all(self, phone: str) -> ProjectPrestador:

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
        row = fetchone(query, (phone,))

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