"""STOPGAP DE TESTE — NÃO É CÓDIGO DE PRODUÇÃO.

Popula `iss_rates` com uma alíquota fixa de 5,0% para todos os códigos nacionais
conhecidos, em vez de buscar as alíquotas reais na ADN (`iss_rate_sync.py`).

Motivo: a reforma recente das regras de ISS do RJ ainda não foi confirmada pelos
parceiros, então a tabela real de alíquotas está indefinida. Sem alíquota vigente
na tabela local, `IssResolutionService.resolve()` levanta `IssResolutionError` e
`ValidationService._iss_ok()` bloqueia a transição COLLECTING -> CONFIRMING —
travando qualquer teste end-to-end.

Este seed destrava o fluxo SEM mexer no código do gate: o caminho de resolução
roda exatamente como em produção (classifica a descrição, consulta a tabela),
só que a tabela responde 5,0% para tudo. É coerente com o resto do sistema hoje,
já que `TomadorManager` ainda emite com a constante `ALIQUOTA_ISS = 5.0` fixa
(ver o TODO em `collecting_service.py`).

`vigencia_inicio` é uma data-sentinela bem antiga ("1900-01-01"): quando o sync
real rodar, as linhas reais terão `vigencia_inicio` recente e vencem estas em
`get_current_rate` (ORDER BY vigencia_inicio DESC), sem colisão de chave.

Uso:      python -m src.workers.iss_rate_seed
Desfazer: python -m src.workers.iss_rate_seed --clear
          (ou: DELETE FROM iss_rates WHERE vigencia_inicio = '1900-01-01';)
"""

import sys

from src.database.db import DB
from src.managers.iss.iss_rate_manager import IssRateManager
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.models.national_service_codes import NATIONAL_SERVICE_CODES
from src.types import IssRate

SEED_ALIQUOTA = 5.0
SEED_VIGENCIA_INICIO = "1900-01-01"


def run_seed(codigo_municipio: str = RJ_CODIGO_MUNICIPIO) -> int:
    manager = IssRateManager()
    rows = [
        IssRate(
            codigo_municipio=codigo_municipio,
            codigo_tributacao_nacional=service_code.codigo,
            aliquota=SEED_ALIQUOTA,
            vigencia_inicio=SEED_VIGENCIA_INICIO,
            vigencia_fim=None,
        )
        for service_code in NATIONAL_SERVICE_CODES
    ]
    manager.upsert_rates(rows)
    return len(rows)


def clear_seed() -> int:
    return DB().exe(
        "DELETE FROM iss_rates WHERE vigencia_inicio = ?", (SEED_VIGENCIA_INICIO,)
    )


if __name__ == "__main__":
    if "--clear" in sys.argv:
        removed = clear_seed()
        print(f"Removidas {removed} linhas de seed de iss_rates.")
        sys.exit(0)

    total = run_seed()
    print(f"Seed de {total} códigos em iss_rates a {SEED_ALIQUOTA}% (STOPGAP DE TESTE).")
    sys.exit(0)
