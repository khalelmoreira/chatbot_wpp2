"""End-to-end: registers a real prestador from scratch (COLLECTING) through to a
working Prestador (ACTIVE), driving every flow module the way the app does —
collecting_flow -> address_flow -> confirming_flow -> project_flow -> certificate_flow
-> certificate_upload_handler. Only external I/O (AI provider, ViaCEP, Notaas) is faked."""

import httpx
import requests
from cryptography.fernet import Fernet

from src.flows.user_flows.address_flow import address_flow
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.confirming_user_flow import confirming_flow
from src.handlers.certificate_handler import certificate_upload_handler
from src.services.ai import ai_client_factory
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import BotaoId, ContextPrestador, MsgType, PrestadorData, User, UserStatus
from src.utils import get_endereco as get_endereco_module


class FakeCepResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json


class FakeNotaasResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json

    def raise_for_status(self) -> None:
        pass


class FakeUploadFile:
    def __init__(self, content: bytes):
        self._content = content

    def read(self) -> bytes:
        return self._content


def _novo_prestador(db, phone: str) -> int:
    return db.insert("prestador", data={"phone": phone, "status": "COLLECTING"}, returning="id")


def _ctx(prestador_id: int, phone: str, status: UserStatus, text: str = "",
         msg_type: MsgType = MsgType.TEXT, button_id: str | None = None) -> ContextPrestador:
    return ContextPrestador(
        user=User(id=prestador_id, phone=phone, status=status),
        text=text, new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=PrestadorData(), msg_type=msg_type, button_id=button_id,
    )


def test_prestador_registration_end_to_end_from_scratch_to_active(db, monkeypatch):
    phone = "5511988887777"
    fernet_key = Fernet.generate_key().decode()
    monkeypatch.setenv("FERNET_KEY", fernet_key)
    monkeypatch.setenv("NTAAS_ORG_TOKEN", "fake_org_token")
    monkeypatch.setenv("APP_DOMAIN", "http://localhost:5000")

    fake_ai = FakeAIClient(extract_json_responses=[
        {
            "cnpj": "11222333000181",
            "razao_social": "Empresa LTDA",
            "email": "a@a.com",
            "regime_tributario": "1",
            "cep": "01310100",
        },
        {"numero": "100"},
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_ai)
    monkeypatch.setattr(
        get_endereco_module.requests, "get",
        lambda url, **kw: FakeCepResp(200, {
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
        }),
    )
    monkeypatch.setattr(requests, "post", lambda url, **kw: FakeNotaasResp(201, {"id": "proj_123"}))

    def _fake_httpx_post(url, **kw):
        if url.endswith("/certificate"):
            return FakeNotaasResp(200, {"status": "ok"})
        if url.endswith("/api-keys"):
            return FakeNotaasResp(200, {"key": "raw_notaas_key_123"})
        raise AssertionError(f"unexpected httpx.post to {url}")

    monkeypatch.setattr(httpx, "post", _fake_httpx_post)

    prestador_id = _novo_prestador(db, phone)

    # COLLECTING -> ADDRESS (auto-lookup via ViaCEP, missing numero)
    collecting_flow(_ctx(
        prestador_id, phone, UserStatus.COLLECTING,
        "CNPJ 11.222.333/0001-81, Empresa LTDA, a@a.com, regime 1, CEP 01310-100",
    ))
    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "ADDRESS"

    # ADDRESS -> CONFIRMING
    address_flow(_ctx(prestador_id, phone, UserStatus.ADDRESS, "numero 100"))
    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CONFIRMING"

    # CONFIRMING -> PROJECT -> CERTIFICATE (project_flow + certificate_flow chained)
    confirming_flow(_ctx(
        prestador_id, phone, UserStatus.CONFIRMING,
        msg_type=MsgType.BUTTON, button_id=BotaoId.PRESTADOR_CONFIRMADO,
    ))
    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CERTIFICATE"
    assert row["ntaas_project_id"] == "proj_123"

    token_row = db.select_one("upload_tokens", where={"prestador_id": prestador_id})
    assert token_row is not None
    assert token_row["used"] == 0

    # CERTIFICATE -> ACTIVE (upload handler: cert sent to Notaas, api-key created and persisted encrypted)
    result = certificate_upload_handler(
        token_row["token"], FakeUploadFile(b"fake-pfx-bytes"), "senha123",
    )
    assert result.status == 200
    assert result.body["success"] is True

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "ACTIVE"
    assert row["certificado_enviado"] == 1
    assert row["ntaas_api_key"] is not None
    assert row["ntaas_api_key"] != "raw_notaas_key_123"  # stored encrypted, never plaintext
    assert Fernet(fernet_key.encode()).decrypt(row["ntaas_api_key"].encode()).decode() == "raw_notaas_key_123"

    used_token_row = db.select_one("upload_tokens", where={"token": token_row["token"]})
    assert used_token_row["used"] == 1

    assert len(fake_ai.extract_calls) == 2
