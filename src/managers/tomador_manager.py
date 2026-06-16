import json
from dataclasses import asdict
import uuid
import hashlib
from src.models.aliquota_iss import ALIQUOTA_ISS
from src.database.db import executar_modif, fetchone, fetchone_modif
from src.types.context_tomador import ContextTomador, DadosTomador, Tomador, Servico, Valores
from src.utils.debug import print_table
from src.managers.conversation_manager import ConversationManager

class TomadorManager:

    def update_nf_from_draft(self, ctx: ContextTomador, conversation: ConversationManager) -> None:

        draft = conversation.get_draft(ctx)

        prestador_id = ctx.user.id
        conversation_id = ctx.conversation_id

        nome        = draft["tomador.nome"]
        cnpj        = draft["tomador.cnpj"]
        descricao   = draft["servico.descricao"]
        valor_total = draft["valores.total"]
        aliquota_iss = ALIQUOTA_ISS

        tomador_id = self._upsert_tomador(prestador_id, nome, cnpj)

        payload = {
            "tomador": {"nome": nome, "cnpj": cnpj},
            "servico": {"descricao": descricao},
            "valores": {"total": valor_total, "aliquotaIss": aliquota_iss},
        }

        payload_enviado = json.dumps(payload, ensure_ascii=False, sort_keys=True)

        idempotency_key = hashlib.sha256(
            f"{payload_enviado}:{prestador_id}".encode()
        ).hexdigest()

        return self._upsert_nf(
            prestador_id, tomador_id, conversation_id,
            idempotency_key, payload_enviado,
            nome, cnpj, descricao, valor_total, aliquota_iss,
        )
    
    def _upsert_tomador(self, prestador_id: int, nome: str, cnpj: str) -> int:

        row = fetchone_modif("""
            INSERT INTO tomador (prestador_id, nome, cnpj)
            VALUES (?, ?, ?)
            ON CONFLICT (prestador_id, cnpj) DO UPDATE SET
                nome       = excluded.nome,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (prestador_id, nome, cnpj),)

        print(f"ROW[ID]: {row["id"]}\n")
        return row["id"]
    
    def _upsert_nf(
            self, prestador_id, tomador_id, conversation_id,
            idempotency_key, payload_enviado,
            nome, cnpj, descricao, valor_total, aliquota_iss
    ) -> int:
        
        row = fetchone_modif("""
            INSERT INTO nfs (
                prestador_id, tomador_id, conversation_id,
                idempotency_key, payload_enviado, nome,
                cnpj, descricao_servico, valor_total, aliquota_iss
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (conversation_id) DO UPDATE SET
                tomador_id        = excluded.tomador_id,
                idempotency_key   = excluded.idempotency_key,
                payload_enviado   = excluded.payload_enviado,
                nome              = excluded.nome,
                cnpj              = excluded.cnpj,
                descricao_servico = excluded.descricao_servico,
                valor_total       = excluded.valor_total,
                aliquota_iss      = excluded.aliquota_iss,
                updated_at        = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            prestador_id, tomador_id, conversation_id,
            idempotency_key, payload_enviado,nome,
            cnpj, descricao, valor_total, aliquota_iss
            ),
        )
        print(f"ROW[ID]: {row["id"]}\n")
        return row["id"]

    def get_db_data(self, ctx: ContextTomador) -> None:

        prestador_id = ctx.user.id

        query = """
            SELECT
                nome,
                cnpj,
                descricao_servico,
                aliquota_iss,
                valor_total
            FROM nfs
            WHERE prestador_id = ?
        """

        result = fetchone(query, (prestador_id,))

        if not result:
            ctx.dados_db = DadosTomador()
            return
        
        nf = result["nf"]

        if not nf:
            ctx.dados_db = DadosTomador()
            return
        
        data = json.loads(nf)

        print(f"nfse_drafts.loads: {data}\n")

        nome = data.get("tomador", {}).get("nome")
        cnpj = data.get("tomador", {}).get("cnpj")

        descricao = data.get("servico", {}).get("descricao")
        total = data.get("valores", {}).get("total")
        aliquotaIss = data.get("valores", {}).get("aliquotaIss")

        ctx.dados_db = DadosTomador(
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
