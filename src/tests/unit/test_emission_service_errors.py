import requests

import src.services.ntaas.emission_service as emission_service_module
from src.services.ntaas.emission_service import emitir_nf
from src.types import NotaasEmissaoPermanenteError, NotaasEmissaoTransitoriaError

PAYLOAD = {"tomador": {"nome": "X", "cnpj": "123"}}


class FakeResp:
    def __init__(self, status_code: int, text: str = "", json_data: dict | None = None):
        self.status_code = status_code
        self.text = text
        self._json = json_data or {}

    def json(self):
        return self._json


def test_emitir_nf_sucesso_retorna_json(monkeypatch):
    monkeypatch.setattr(
        emission_service_module.requests, "post",
        lambda *a, **kw: FakeResp(202, json_data={"invoiceId": "abc"}),
    )
    assert emitir_nf(PAYLOAD) == {"invoiceId": "abc"}


def test_emitir_nf_4xx_e_permanente(monkeypatch):
    monkeypatch.setattr(
        emission_service_module.requests, "post",
        lambda *a, **kw: FakeResp(422, text="cidade não suportada"),
    )
    try:
        emitir_nf(PAYLOAD)
        assert False, "deveria ter levantado NotaasEmissaoPermanenteError"
    except NotaasEmissaoPermanenteError:
        pass


def test_emitir_nf_5xx_e_transitorio(monkeypatch):
    monkeypatch.setattr(
        emission_service_module.requests, "post",
        lambda *a, **kw: FakeResp(503, text="fora do ar"),
    )
    try:
        emitir_nf(PAYLOAD)
        assert False, "deveria ter levantado NotaasEmissaoTransitoriaError"
    except NotaasEmissaoTransitoriaError:
        pass


def test_emitir_nf_erro_de_rede_e_transitorio(monkeypatch):
    def _raise(*a, **kw):
        raise requests.ConnectionError("sem rota até o host")

    monkeypatch.setattr(emission_service_module.requests, "post", _raise)

    try:
        emitir_nf(PAYLOAD)
        assert False, "deveria ter levantado NotaasEmissaoTransitoriaError"
    except NotaasEmissaoTransitoriaError:
        pass
