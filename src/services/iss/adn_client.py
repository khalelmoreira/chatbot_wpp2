"""Cliente para a API de Parâmetros Municipais do Sistema Nacional NFS-e (ADN).

Autenticação por mTLS com um certificado A1 da empresa (não do prestador — ver
task-aliquota-iss-rj.md e a decisão registrada no plano de implementação). O shape
exato da resposta não pôde ser confirmado por documentação pública (o Swagger da
API está atrás do mesmo mTLS), então o parsing aqui valida os campos esperados e
falha alto (IssRateSyncError) em vez de adivinhar — ajustar contra a resposta real
de homologação na primeira execução real do sync.
"""

import logging
import os
import tempfile
from pathlib import Path

import httpx
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    pkcs12,
)

from src.types import IssRate, IssRateSyncError

logger = logging.getLogger(__name__)

_HOMOLOGACAO_BASE_URL = "https://adn.producaorestrita.nfse.gov.br/parametrizacao"
_PRODUCAO_BASE_URL = "https://adn.nfse.gov.br/parametrizacao"


def _base_url() -> str:
    ambiente = os.environ.get("ISS_ADN_ENV", "homologacao")
    return _PRODUCAO_BASE_URL if ambiente == "producao" else _HOMOLOGACAO_BASE_URL


def _load_client_cert() -> tuple[str, str]:
    """Converte o .pfx apontado por ISS_ADN_CERT_PATH em um par de arquivos PEM
    (cert, key) temporários — httpx.Client(cert=...) espera caminhos PEM, não pfx."""

    pfx_path = Path(os.environ["ISS_ADN_CERT_PATH"])
    password = os.environ["ISS_ADN_CERT_PASSWORD"].encode()

    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        pfx_path.read_bytes(), password,
    )
    if private_key is None or certificate is None:
        raise IssRateSyncError(f"Certificado inválido/incompleto em {pfx_path}")

    tmp_dir = tempfile.mkdtemp(prefix="iss_adn_cert_")
    cert_path = Path(tmp_dir) / "cert.pem"
    key_path = Path(tmp_dir) / "key.pem"

    cert_path.write_bytes(certificate.public_bytes(Encoding.PEM))
    key_path.write_bytes(
        private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )
    os.chmod(key_path, 0o600)

    return str(cert_path), str(key_path)


class AdnClient:
    def __init__(self):
        cert_path, key_path = _load_client_cert()
        self._client = httpx.Client(
            base_url=_base_url(),
            cert=(cert_path, key_path),
            timeout=20.0,
        )

    def fetch_rates(self, codigo_municipio: str, codigo_tributacao_nacional: str) -> list[IssRate]:
        resp = self._client.get(
            f"/parametros_municipais/{codigo_municipio}/{codigo_tributacao_nacional}"
        )
        resp.raise_for_status()
        payload = resp.json()

        return [
            self._parse_rate(codigo_municipio, codigo_tributacao_nacional, item)
            for item in self._extract_items(payload)
        ]

    def _extract_items(self, payload: object) -> list[dict]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("aliquotas", "items", "data"):
                items = payload.get(key)
                if isinstance(items, list):
                    return items
        raise IssRateSyncError(f"Formato de resposta inesperado da API de parâmetros municipais: {payload!r}")

    def _parse_rate(self, codigo_municipio: str, codigo_tributacao_nacional: str, item: dict) -> IssRate:
        try:
            aliquota = float(item["aliquota"])
            vigencia_inicio = str(item["dataInicioVigencia"])
        except (KeyError, TypeError, ValueError) as e:
            raise IssRateSyncError(f"Item de alíquota com campos inesperados: {item!r}") from e

        vigencia_fim = item.get("dataFimVigencia")

        return IssRate(
            codigo_municipio=codigo_municipio,
            codigo_tributacao_nacional=codigo_tributacao_nacional,
            aliquota=aliquota,
            vigencia_inicio=vigencia_inicio,
            vigencia_fim=str(vigencia_fim) if vigencia_fim else None,
        )
