import logging

import requests

logger = logging.getLogger(__name__)


def get_cnpj_info(cnpj: str) -> dict | None:

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

    try:
        response = requests.get(url, timeout=5)

    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    logger.debug("brasilapi cnpj response.json=%s", data)

    return data
