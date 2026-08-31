"""Carga da tabela de alíquotas de ISS do RJ (src/models/iss_rates_rj.py) na
tabela local `iss_rates`.

Fora do hot path da emissão: roda uma vez, manualmente, quando a tabela muda —
não é um job recorrente (as alíquotas do RJ são estáveis e cada mudança já passa
por PR + deploy). `IssResolutionService.resolve()` lê só de `iss_rates`, nunca
desta fonte diretamente.

`vigencia_inicio` de todas as linhas é RJ_ISS_VIGENCIA_INICIO (a data em que os
parceiros confirmaram a tabela), não a data em que o script roda — a vigência é
uma propriedade do dado, não da execução. Reexecutar é idempotente (upsert pela
chave (municipio, codigo, vigencia_inicio)).

Uso:      python -m src.workers.iss_rate_load
Desfazer: python -m src.workers.iss_rate_load --clear
"""

import sys

from src.database.db import DB
from src.managers.iss.iss_rate_manager import IssRateManager
from src.models.iss_rates_rj import RJ_ISS_RATES, RJ_ISS_VIGENCIA_INICIO
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.types import IssRate


def run_load(codigo_municipio: str = RJ_CODIGO_MUNICIPIO) -> int:
    manager = IssRateManager()
    rows = [
        IssRate(
            codigo_municipio=codigo_municipio,
            codigo_tributacao_nacional=r.codigo_tributacao_nacional,
            aliquota=r.aliquota,
            vigencia_inicio=RJ_ISS_VIGENCIA_INICIO,
            vigencia_fim=None,
        )
        for r in RJ_ISS_RATES
    ]
    manager.upsert_rates(rows)
    return len(rows)


def clear_load(codigo_municipio: str = RJ_CODIGO_MUNICIPIO) -> int:
    return DB().exe(
        "DELETE FROM iss_rates WHERE codigo_municipio = ? AND vigencia_inicio = ?",
        (codigo_municipio, RJ_ISS_VIGENCIA_INICIO),
    )


if __name__ == "__main__":
    if "--clear" in sys.argv:
        removed = clear_load()
        print(f"Removidas {removed} linhas de iss_rates (RJ, vigência {RJ_ISS_VIGENCIA_INICIO}).")
        sys.exit(0)

    total = run_load()
    print(f"Carregados {total} códigos em iss_rates (RJ, vigência {RJ_ISS_VIGENCIA_INICIO}).")
    sys.exit(0)
