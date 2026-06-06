import json
from dataclasses import asdict
import uuid
from src.database.db import executar_modif, fetchone
from src.types.context_nfse import ContextNfse, DadosNfse, Tomador, Servico, Valores
from src.utils.debug import print_table

class NFSeManager:

    def get_draft(self, ctx: ContextNfse) -> None:

        phone = ctx.user.phone

        query = """
            SELECT nf
            FROM nfse_drafts
            WHERE phone = ?
        """

        result = fetchone(query, (phone,))

        if not result:
            ctx.dados_db = DadosNfse()
            return
        
        nf = result["nf"]

        if not nf:
            ctx.dados_db = DadosNfse()
            return
        
        data = json.loads(nf)

        print(f"nfse_drafts.loads: {data}\n")

        nome = data.get("tomador", {}).get("nome")
        cnpj = data.get("tomador", {}).get("cnpj")

        descricao = data.get("servico", {}).get("descricao")
        total = data.get("valores", {}).get("total")
        aliquotaIss = data.get("valores", {}).get("aliquotaIss")

        ctx.dados_db = DadosNfse(
            tomador=Tomador(
                nome=nome,
                cnpj=cnpj
            ),
            servico=Servico(
                descricao=descricao
            ),
            valores=Valores(
                total=total,
                aliquotaIss=aliquotaIss
            )
        )

    def delete_nfse_draft(self, ctx: ContextNfse) -> None:

        phone = ctx.user.phone

        query = """
            DELETE FROM nfse_drafts
            WHERE phone = ?
        """
        executar_modif(
            query,
            (phone,)
        )
        
        print_table("nfse_drafts")

    def add_fila(self, ctx: ContextNfse) -> None:

        dados_nf = ctx.validacao.validos

        query = """
        INSERT INTO fila_emissao (
            payload,
            idempotency_key
        )
        VALUES (?, ?)
        """

        payload = json.dumps(dados_nf, ensure_ascii=False)
        idempotency_key = str(uuid.uuid4())

        executar_modif(
            query,
            (payload, idempotency_key)
        )

        print("\nadicionado a fila de emissao\n")
        print_table("fila_emissao")

    def update_draft(self, ctx: ContextNfse) -> None:

        phone = ctx.user.phone

        print(f"ATUALIZA DADOS DA TABLE nfse_drafts.\n")
        print(f"ANTES:\n")
        print_table("nfse_drafts")

        query = """
            INSERT INTO nfse_drafts (
                phone,
                nf,
                updated_at
            )
            VALUES (?, ?, datetime('now'))

            ON CONFLICT(phone)
            DO UPDATE SET
                nf = excluded.nf,
                updated_at = datetime('now')
        """

        executar_modif(
            query,
            (
                phone,
                json.dumps(asdict(ctx.dados_novos))
            )
        )
        print(f"DEPOIS:\n")
        print_table("nfse_drafts")