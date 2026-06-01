import json
from dataclasses import asdict
import uuid
from src.repositories.db import executar_modif, fetchone
from src.types.context_nfse import ContextNfse, DadosNfse, Tomador, Servico, Valores
from src.utils.debug import print_table

def atualizar_nf_parcial(ctx: ContextNfse) -> None:

    phone = ctx.user.phone

    print(f"ATUALIZA DADOS DA TABLE nf_parcial.\n")
    print(f"ANTES:\n")
    print_table("nf_parcial")

    query = """
        INSERT INTO nf_parcial (
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
    print_table("nf_parcial")

def buscar_nf_parcial(ctx: ContextNfse) -> None:

    phone = ctx.user.phone

    query = """
        SELECT nf
        FROM nf_parcial
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

    print(f"nf_parcial.loads: {data}\n")

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

def limpar_nf_parcial(ctx: ContextNfse) -> None:

    phone = ctx.user.phone

    query = """
        DELETE FROM nf_parcial
        WHERE phone = ?
    """
    executar_modif(
        query,
        (phone,)
    )
    
    print_table("nf_parcial")

def adicionar_fila_emissao(ctx: ContextNfse) -> None:

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