import requests

from src.flows.user_flows.project_flow import project_flow
from src.types import ContextPrestador, MsgType, PrestadorData, User, UserStatus


class FakeResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json

    def raise_for_status(self) -> None:
        pass


def _novo_prestador(db, status: str) -> int:
    return db.insert(
        "prestador",
        data={
            "phone": "5511999999999", "status": status, "email": "a@a.com",
            "cnpj": "11222333000181", "razao_social": "Empresa LTDA",
            "regime_tributario": "1", "cep": "01310100",
            "address_logradouro": "Av Paulista", "address_numero": "100",
            "address_bairro": "Bela Vista", "address_cidade": "São Paulo", "address_uf": "SP",
        },
        returning="id",
    )


def _ctx(prestador_id: int) -> ContextPrestador:
    return ContextPrestador(
        user=User(id=prestador_id, phone="5511999999999", status=UserStatus.PROJECT),
        text="", new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=PrestadorData(), msg_type=MsgType.TEXT,
    )


def test_project_flow_cria_projeto_e_avanca_para_certificate(db, monkeypatch):
    monkeypatch.setenv("NTAAS_ORG_TOKEN", "fake_org_token")
    monkeypatch.setenv("APP_DOMAIN", "http://localhost:5000")
    monkeypatch.setattr(requests, "post", lambda url, **kw: FakeResp(201, {"id": "proj_123"}))

    prestador_id = _novo_prestador(db, "PROJECT")
    project_flow(_ctx(prestador_id))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CERTIFICATE"
    assert row["ntaas_project_id"] == "proj_123"

    token_row = db.select_one("upload_tokens", where={"prestador_id": prestador_id})
    assert token_row is not None
    assert token_row["project_id"] == "proj_123"


def test_project_flow_reentrada_reaproveita_projeto_existente(db, monkeypatch):
    """Se o projeto já existe na Notaas (409), reentrar no PROJECT deve avançar mesmo assim, não travar."""
    monkeypatch.setenv("NTAAS_ORG_TOKEN", "fake_org_token")
    monkeypatch.setenv("APP_DOMAIN", "http://localhost:5000")
    monkeypatch.setattr(
        requests, "post",
        lambda url, **kw: FakeResp(409, {"existingProjectId": "proj_existente"}),
    )

    prestador_id = _novo_prestador(db, "PROJECT")
    project_flow(_ctx(prestador_id))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CERTIFICATE"
    assert row["ntaas_project_id"] == "proj_existente"
