from typing import Any
from src.types.context_tomador import DadosTomador, ContextTomador, Tomador, Servico, Valores

def unpack_dados_db(data: dict[str, Any], ctx: ContextTomador) -> DadosTomador:

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