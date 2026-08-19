"""Sync diário das alíquotas de ISS (RJ). Fora do hot path da emissão — roda como
job independente, não como thread em segundo plano do app (ao contrário de
EmissaoWorker/PollingWorker): um job de uma vez por dia não ganha nada de um loop
de sleep em processo, que só desalinha em cada restart/deploy. Pensado para ser
disparado por um timer do systemd na VPS (setup de infra, não código).

Uso manual: python -m src.workers.iss_rate_sync
"""

import logging
import sys

from src.managers.iss.iss_rate_manager import IssRateManager
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.models.national_service_codes import NATIONAL_SERVICE_CODES
from src.services.iss.adn_client import AdnClient

logger = logging.getLogger(__name__)


def run_sync(codigo_municipio: str = RJ_CODIGO_MUNICIPIO) -> int:
    """Busca a alíquota vigente de cada código nacional conhecido e faz upsert
    local. Retorna quantos códigos foram sincronizados com sucesso; erros por
    código são logados e não interrompem os demais."""

    client = AdnClient()
    manager = IssRateManager()
    synced = 0

    for service_code in NATIONAL_SERVICE_CODES:
        try:
            rates = client.fetch_rates(codigo_municipio, service_code.codigo)
            manager.upsert_rates(rates)
            synced += 1
        except Exception:
            logger.exception(
                "Falha ao sincronizar alíquota codigo=%s municipio=%s",
                service_code.codigo, codigo_municipio,
            )

    return synced


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    total = run_sync()
    print(f"Sincronizados {total}/{len(NATIONAL_SERVICE_CODES)} códigos.")
    sys.exit(0 if total > 0 else 1)
