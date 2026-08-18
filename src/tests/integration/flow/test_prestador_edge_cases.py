"""Edge cases for prestador registration (Week 2 checklist): a partially registered
prestador spread across messages, divergent data re-sent across attempts (merge must
keep the latest value), and an invalid tax regime (must block progress and be reported,
never silently dropped)."""

from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.services.ai import ai_client_factory
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import ContextPrestador, MsgType, PrestadorData, User, UserStatus
from src.utils import get_endereco as get_endereco_module


class FakeCepResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json


def _novo_prestador(db, phone: str) -> int:
    return db.insert("prestador", data={"phone": phone, "status": "COLLECTING"}, returning="id")


def _ctx(prestador_id: int, phone: str, text: str) -> ContextPrestador:
    return ContextPrestador(
        user=User(id=prestador_id, phone=phone, status=UserStatus.COLLECTING),
        text=text, new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=PrestadorData(), msg_type=MsgType.TEXT,
    )


def test_partial_registration_stays_in_collecting_until_all_fields_present(db, monkeypatch):
    phone = "5511911112222"
    prestador_id = _novo_prestador(db, phone)

    fake_ai = FakeAIClient(extract_json_responses=[
        {"razao_social": "Empresa LTDA", "cnpj": "11222333000181"},
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_ai)

    collecting_flow(_ctx(prestador_id, phone, "sou a Empresa LTDA, CNPJ 11.222.333/0001-81"))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "COLLECTING"
    assert row["razao_social"] == "Empresa LTDA"
    assert row["cnpj"] == "11222333000181"
    assert row["email"] is None
    assert row["cep"] is None


def test_divergent_data_across_attempts_keeps_latest_value(db, monkeypatch):
    """User corrects a field in a later message — merge must overwrite, not keep the first value."""
    phone = "5511922223333"
    prestador_id = _novo_prestador(db, phone)

    fake_ai = FakeAIClient(extract_json_responses=[
        {"razao_social": "Empresa Antiga LTDA", "cnpj": "11222333000181", "email": "antigo@a.com"},
        {"email": "novo@a.com", "razao_social": "Empresa Nova LTDA"},
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_ai)

    collecting_flow(_ctx(prestador_id, phone, "Empresa Antiga LTDA, CNPJ 11.222.333/0001-81, antigo@a.com"))
    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["razao_social"] == "Empresa Antiga LTDA"
    assert row["email"] == "antigo@a.com"

    collecting_flow(_ctx(prestador_id, phone, "corrigindo: na verdade é Empresa Nova LTDA, email novo@a.com"))
    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["razao_social"] == "Empresa Nova LTDA"
    assert row["email"] == "novo@a.com"
    assert row["cnpj"] == "11222333000181"  # untouched field from the first message survives the merge


def test_invalid_tax_regime_blocks_progress_and_is_never_persisted(db, monkeypatch):
    """regime_tributario='9' has no valid mapping. Even though every other field is valid,
    the prestador must NOT be treated as complete, must NOT advance past COLLECTING, and
    the invalid field must never silently end up NULL-and-forgotten."""
    phone = "5511933334444"
    prestador_id = _novo_prestador(db, phone)

    fake_ai = FakeAIClient(extract_json_responses=[
        {
            "cnpj": "11222333000181",
            "razao_social": "Empresa LTDA",
            "email": "a@a.com",
            "regime_tributario": "9",
            "cep": "01310100",
        },
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_ai)

    collecting_flow(_ctx(
        prestador_id, phone,
        "Empresa LTDA, CNPJ 11.222.333/0001-81, a@a.com, regime tributario 9, CEP 01310-100",
    ))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "COLLECTING"  # never advanced to ADDRESS
    assert row["regime_tributario"] is None
    # the rest of the message was still valid, so it isn't lost while the user fixes the regime
    assert row["razao_social"] == "Empresa LTDA"
    assert row["cnpj"] == "11222333000181"

    # user corrects it in the next message
    fake_ai._extract_json_responses.append({"regime_tributario": "1"})
    monkeypatch.setattr(
        get_endereco_module.requests, "get",
        lambda url, **kw: FakeCepResp(200, {
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
        }),
    )
    collecting_flow(_ctx(prestador_id, phone, "o regime é 1, simples nacional"))

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "ADDRESS"
    assert row["regime_tributario"] == "1"
