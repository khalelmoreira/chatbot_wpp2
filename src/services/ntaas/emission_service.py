import logging
import os

import requests
from dotenv import load_dotenv

from src.types import NotaasEmissaoPermanenteError, NotaasEmissaoTransitoriaError

load_dotenv()
logger = logging.getLogger(__name__)
API_KEY = os.getenv("NOTAAS_API_KEY")

TIMEOUT_SEGUNDOS = 15


def emitir_nf(dados):
    """Erros 4xx (payload rejeitado — CNPJ inválido, cidade não suportada etc.)
    viram NotaasEmissaoPermanenteError: repetir sem mudar o payload só repete o
    erro, então o worker não deve reenfileirar. Timeout/erro de rede/5xx viram
    NotaasEmissaoTransitoriaError: podem ser uma instabilidade passageira (ex.:
    prefeitura fora do ar) e seguem elegíveis para retry com backoff."""

    logger.debug("emitir_nf: payload=%s", dict(dados))

    url = "https://platform.notaas.com.br/api/v1/emitir"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    try:
        response = requests.post(url, json=dados, headers=headers, timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException as e:
        raise NotaasEmissaoTransitoriaError(f"Falha de rede ao emitir NF-e: {e}") from e

    logger.debug("emitir_nf: response=%s", response)

    if response.status_code in (200, 201, 202):
        return response.json()

    if 400 <= response.status_code < 500:
        raise NotaasEmissaoPermanenteError(
            f"Notaas rejeitou o payload ({response.status_code}): {response.text}"
        )

    raise NotaasEmissaoTransitoriaError(
        f"Erro no servidor da Notaas ({response.status_code}): {response.text}"
    )
