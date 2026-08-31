import hashlib
import json
import logging
from dataclasses import asdict

from src.database.db import DB
from src.types import ContextTomador, InvalidTransactionError, TomadorData

logger = logging.getLogger(__name__)

class TomadorManager:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.db  = DB()

    def update_nf_from_draft(self, draft: dict) -> int | None:

        prestador_id = self.ctx.user.id
        conv_id = self.ctx.conv_id

        data = TomadorData.from_dict(draft)

        nome          = data.tomador.nome
        cnpj          = data.tomador.cnpj
        descricao     = data.servico.descricao
        valor_total   = data.valores.total
        codigo_servico = data.servico.codigo
        aliquota_iss  = data.valores.aliquotaIss

        # _iss_ok() (checkpoint pré-emissão) só deixa a conversa chegar a CONFIRMING
        # depois de resolver alíquota e cTribNac no draft. Se faltam aqui, o draft
        # foi montado por fora do fluxo — falha explícita, não um default silencioso.
        if aliquota_iss is None or codigo_servico is None:
            raise InvalidTransactionError(
                f"draft sem ISS resolvido (aliquota={aliquota_iss}, codigo={codigo_servico}) "
                f"na emissão da conv {conv_id}"
            )

        tomador_id = self._upsert_tomador(prestador_id, nome, cnpj) # type: ignore

        payload = asdict(data)
        payload_enviado = json.dumps(payload, ensure_ascii=False, sort_keys=True)

        idempotency_key = hashlib.sha256(
            f"{payload_enviado}:{prestador_id}".encode()
        ).hexdigest()

        return self._upsert_nf(
            prestador_id, tomador_id, conv_id,
            idempotency_key, payload_enviado,
            nome, cnpj, descricao, valor_total, aliquota_iss, codigo_servico,
        )
    
    def _upsert_tomador(self, prestador_id: int, nome: str, cnpj: str) -> int:

        row = self.db.fetchone_exe("""
            INSERT INTO tomador (prestador_id, name, cnpj)
            VALUES (?, ?, ?)
            ON CONFLICT (prestador_id, cnpj) DO UPDATE SET
                name       = excluded.name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (prestador_id, nome, cnpj),)

        logger.debug("tomador upsert id=%s", row['id'])
        return row["id"]
    
    def _upsert_nf(
            self, prestador_id, tomador_id, conv_id,
            idempotency_key, payload_enviado,
            nome, cnpj, descricao, valor_total, aliquota_iss, codigo_servico
    ) -> int | None:

        row = self.db.fetchone_exe("""
            INSERT INTO nfs (
                prestador_id, tomador_id, conv_id,
                idempotency_key, payload_enviado, nome,
                cnpj, descricao_servico, valor_total, aliquota_iss, codigo_servico
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (conv_id) DO UPDATE SET
                tomador_id        = excluded.tomador_id,
                idempotency_key   = excluded.idempotency_key,
                payload_enviado   = excluded.payload_enviado,
                nome              = excluded.nome,
                cnpj              = excluded.cnpj,
                descricao_servico = excluded.descricao_servico,
                valor_total       = excluded.valor_total,
                aliquota_iss      = excluded.aliquota_iss,
                codigo_servico    = excluded.codigo_servico,
                status            = 'QUEUED',
                tentativas        = 0,
                erro_msg          = NULL,
                erro_code         = NULL,
                invoice_id        = NULL,
                updated_at        = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            prestador_id, tomador_id, conv_id,
            idempotency_key, payload_enviado,nome,
            cnpj, descricao, valor_total, aliquota_iss, codigo_servico
            ),
        )
        if row is None:
            return None
        logger.debug("nf upsert id=%s", row["id"])
        return row["id"]
