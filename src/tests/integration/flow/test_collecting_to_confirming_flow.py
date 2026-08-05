from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.address_flow import address_flow
from src.services.ai.ai_client import GemmaClient
from src.utils import get_endereco as get_endereco_module
from src.types import ContextPrestador, PrestadorData, Address, User, UserStatus, MsgType


class FakeCepResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json


def _novo_prestador(db, phone: str) -> int:
    return db.insert(
        "prestador",
        data={"phone": phone, "status": "COLLECTING"},
        returning="id",
    )


def _ctx(prestador_id: int, phone: str, status: UserStatus, text: str) -> ContextPrestador:
    return ContextPrestador(
        user=User(id=prestador_id, phone=phone, status=status),
        text=text, new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=PrestadorData(), msg_type=MsgType.TEXT,
    )


def test_collecting_to_confirming_flow_end_to_end(db, monkeypatch):
    """COLLECTING (dados completos + CEP) -> ADDRESS (auto-lookup ViaCEP, falta numero)
    -> ADDRESS (usuario envia numero) -> CONFIRMING."""

    phone = "5511988887777"
    prestador_id = _novo_prestador(db, phone)

    extract_calls: list[str] = []

    def fake_extract_json(self, system_prompt: str, user_msg: str) -> dict:
        extract_calls.append(user_msg)
        if len(extract_calls) == 1:
            return {
                "cnpj": "11222333000181",
                "razao_social": "Empresa LTDA",
                "email": "a@a.com",
                "regime_tributario": "1",
                "cep": "01310100",
            }
        return {"numero": "100"}

    monkeypatch.setattr(GemmaClient, "extract_json", fake_extract_json)
    monkeypatch.setattr(
        get_endereco_module.requests, "get",
        lambda url, **kw: FakeCepResp(200, {
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
        }),
    )

    collecting_flow(_ctx(
        prestador_id, phone, UserStatus.COLLECTING,
        "CNPJ 11.222.333/0001-81, Empresa LTDA, a@a.com, regime 1, CEP 01310-100",
    ))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "ADDRESS"
    assert row["cnpj"] == "11222333000181"
    assert row["cep"] == "01310100"
    assert row["address_logradouro"] == "Avenida Paulista"
    assert row["address_bairro"] == "Bela Vista"
    assert row["address_cidade"] == "São Paulo"
    assert row["address_uf"] == "SP"
    assert row["address_numero"] is None

    address_flow(_ctx(prestador_id, phone, UserStatus.ADDRESS, "numero 100"))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CONFIRMING"
    assert row["address_numero"] == "100"
    assert row["address_logradouro"] == "Avenida Paulista"

    assert len(extract_calls) == 2
