from src.types.context_prestador import ContextPrestador, DadosPrestador
from src.database.db import executar_modif, fetchone
import sqlite3
from src.database.get_connection import get_connection

class PrestadorManager:

    CAMPOS_EDITAVEIS = [
        "razao_social",
        "cnpj",
        "email",
        "regime_tributario",
        "cep",
        "inscricao_municipal",
    ]

    # SALVA DADOS_NOVOS NO DB

    def update_validos(self, ctx: ContextPrestador) -> None:

        print(f"UPDATE VALIDOS\n")

        phone = ctx.user.phone
        validos = ctx.validacao.validos

        print(f"VALIDACAO: {ctx.validacao}\n")
        print(f"VALIDOS: {validos}\n")
        
        campos_sql = []
        valores = []

        for campo, valor in validos.items():
            
            if campo not in self.CAMPOS_EDITAVEIS:
                continue

            campos_sql.append(f"{campo} = ?")
            valores.append(valor)

        if not campos_sql:
            return
        
        query = f"""
            UPDATE prestador
            SET {", ".join(campos_sql)}
            WHERE phone = ?
        """

        valores.append(phone)

        executar_modif(query, tuple(valores))

        with get_connection() as conn:
            cursor = conn.cursor()
        print(f"LINHAS AFETADAS: {cursor.rowcount}")

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

            print(f"SEM DADOS DO PRESTADOR\n")

            return

        ctx.dados_db = DadosPrestador(
            razao_social=row["razao_social"],
            cnpj=row["cnpj"],
            email=row["email"],
            regime_tributario=row["regime_tributario"],
            cep=row["cep"],
            inscricao_municipal=row["inscricao_municipal"],
        )

        print(f"DADOS SALVOS PRESTADOR: {ctx.dados_db}\n")