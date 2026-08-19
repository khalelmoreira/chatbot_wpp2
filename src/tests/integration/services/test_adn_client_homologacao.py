"""Teste de integração real contra a API de Parâmetros Municipais (ADN) em
homologação. Requer um certificado A1 válido — pulado quando ISS_ADN_CERT_PATH
não está configurado (CI sem o certificado, por exemplo), em vez de falhar.
"""

import os

import pytest

from src.models.municipios import RJ_CODIGO_MUNICIPIO

pytestmark = pytest.mark.skipif(
    not os.environ.get("ISS_ADN_CERT_PATH"),
    reason="ISS_ADN_CERT_PATH não configurado — pulando teste contra homologação real.",
)


def test_fetch_rates_against_homologacao():
    from src.services.iss.adn_client import AdnClient

    client = AdnClient()
    rates = client.fetch_rates(RJ_CODIGO_MUNICIPIO, "010601")

    assert isinstance(rates, list)
    for rate in rates:
        assert rate.aliquota >= 0
        assert rate.vigencia_inicio
