import json
from dataclasses import asdict
import uuid
import hashlib
from src.models.aliquota_iss_constant import ALIQUOTA_ISS
from src.database.db import DB
from src.types import ContextTomador, TomadorData
from src.utils.debug import print_table

class TomadorManager:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.db  = DB()

    def update_nf_from_draft(self, draft: dict) -> None:

        prestador_id = self.ctx.user.id
        conversation_id = self.ctx.conversation_id

        data = TomadorData.from_dict(draft)

        nome         = data.tomador.nome
        cnpj         = data.tomador.cnpj
        descricao    = data.servico.descricao
        valor_total  = data.valores.total
        aliquota_iss = ALIQUOTA_ISS

        tomador_id = self._upsert_tomador(prestador_id, nome, cnpj)

        payload = asdict(data)
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

        row = self.db.fetchone_modif("""
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
        
        row = self.db.fetchone_modif("""
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

    def get_db_data(self) -> None:
        result = self.db.select(
            "nfs",
            columns="nome, cnpj, descricao_servico, aliquota_iss, valor_total",
            where={"prestador_id": self.ctx.user.id}
        )

        if not result[0]:
            self.ctx.db_data = TomadorData()
            return
        
        nf = result[0]["nf"]

        if not nf:
            self.ctx.db_data = TomadorData()
            return
        
        data = json.loads(nf)

        print(f"nfse_drafts.loads: {data}\n")
        self.ctx.db_data = TomadorData.from_dict(data)
