import json
from dataclasses import asdict
import uuid
from src.database.db import executar_modif, fetchone
from chatbot_wpp2.src.types.context_tomador import ContextTomador, DadosTomador, Tomador, Servico, Valores
from src.utils.debug import print_table

class TomadorManager:

    _VALIDOS_TOMADOR: dict[str, str] = {
        "tomador.nome": "nome",
        "tomador.cnpj": "cnpj",
    }

    _VALIDOS_NF: dict[str, str] = {
        "servico.descricao": "descricao_servico",
        "valores.total": "valor_total",
    }

    def update_validos(self, ctx: ContextTomador) -> None:
        
        validos = ctx.validacao.validos
        tomador_id = self._upsert_tomador(prestador_id, validos)
        self._insert_nota(prestador_id, tomador_id, ctx, validos)

    def _upsert_tomador(self, prestador_id: int, validos: dict) -> int:

        campos_fixos = {"prestador_id": prestador_id}

        campos_dinamicos = {
            col: validos[chave]
            for chave, col in self._VALIDOS_TOMADOR.items()
            if chave in validos
        }

        all_campos = {**campos_fixos, **campos_dinamicos}
        colunas = list(all_campos.keys())
        valores = list(all_campos.values())

        set_clause = ", ".join(
            f"{c} = exclued.{c}"
            for c in colunas
            if c != "prestador_id"
        )

        query = f"""
            INSERT INTO tomador ({', '.join(colunas)})
            VALUES ({', '.join('?' * len(colunas))})
            ON CONFLICT(prestador_id, cnpj) DO UPDATE SET
                {set_clause}
            RETURNING id
        """

        row = fetchone(query, tuple(valores))
        return row
    
    def _insert_nf(
            self,
            prestador_id: int,
            tomador_id: int,
            ctx: ContextTomador,
            validos: dict,
    ) -> None:

        campos_fixos = {
        "prestador_id":    prestador_id,
        "tomador_id":      tomador_id,
        "idempotency_key": ctx.idempotency_key,
        "payload_enviado": json.dumps(asdict(ctx.dados_completos)),
        "status":          "queued",
        }

        campos_dinamicos = {
        col: validos[chave]
        for chave, col in self._VALIDOS_NF.items()
        if chave in validos
        }

        all_campos = {**campos_fixos, **campos_dinamicos}
        colunas = list(all_campos.keys())
        valores = list(all_campos.values())

        # Chaves estruturais nunca são sobrescritas no conflito
        IMUTAVEIS = {"prestador_id", "tomador_id", "idempotency_key", "status"}
        set_clause = ", ".join(
            f"{c} = excluded.{c}"
            for c in colunas
            if c not in IMUTAVEIS
        )
        set_clause += ", updated_at = datetime('now')"

        query = f"""
            INSERT INTO nfs ({', '.join(colunas)})
            VALUES ({', '.join('?' * len(colunas))})
            ON CONFLICT (idempotency_key) DO UPDATE SET
                {set_clause}
        """

        executar_modif(query, tuple(valores))

    def get_db_data(self, ctx: ContextTomador) -> None:

        phone = ctx.user.phone

        query = """
            SELECT nf
            FROM nfse_drafts
            WHERE phone = ?
        """

        result = fetchone(query, (phone,))

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

    def delete_nfse_draft(self, ctx: ContextTomador) -> None:

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

    def add_fila(self, ctx: ContextTomador) -> None:

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
