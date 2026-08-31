import json

from src.flows.active_flows.active_flow import active_flow
from src.flows.active_flows.collecting_flow import collecting_flow
from src.flows.active_flows.confirming_flow import confirming_flow
from src.managers.conversations.conv_manager import ConvManager
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.services.active.collecting import collecting_service
from src.services.ai import ai_client_factory
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import BotaoId, ContextTomador, MsgType, TomadorData, User, UserStatus


def _novo_prestador(db, phone: str) -> int:
    return db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")


def _nova_conversa(db, prestador_id: int, phone: str, status: str, draft: dict | None = None) -> int:
    return db.insert(
        "conversations",
        data={
            "prestador_id": prestador_id,
            "phone": phone,
            "status": status,
            "draft_json": json.dumps(draft or {}),
        },
        returning="id",
    )


def _ctx(
    prestador_id: int, phone: str, text: str = "",
    conv_id: int | None = None, msg_type: MsgType = MsgType.TEXT, button_id: str | None = None,
) -> ContextTomador:
    return ContextTomador(
        user=User(id=prestador_id, phone=phone, status=UserStatus.ACTIVE),
        text=text, new_data=TomadorData(), db_data=TomadorData(),
        merged=TomadorData(), valid=TomadorData(), msg_type=msg_type,
        button_id=button_id, conv_id=conv_id,
    )


def test_active_flow_with_no_conversation_creates_one_on_emitir_intent(db, monkeypatch):
    """No active conversation -> idle_flow -> classify EMITIR -> a COLLECTING conversation
    is created and collecting_flow is handed off to."""
    phone = "5511911112222"
    prestador_id = _novo_prestador(db, phone)

    fake_client = FakeAIClient(extract_json_responses=[{"value": "EMITIR"}])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_client)

    handed_off = []
    monkeypatch.setattr(
        "src.services.active.intent_service.collecting_flow",
        lambda ctx, conv: handed_off.append(ctx.conv_id),
    )

    active_flow(_ctx(prestador_id, phone, "quero emitir uma nota"))

    row = db.select_one("conversations", where={"prestador_id": prestador_id})
    assert row["status"] == "COLLECTING"
    assert handed_off == [row["id"]]


def test_confirming_corrigir_returns_conversation_to_collecting(db):
    phone = "5511933334444"
    prestador_id = _novo_prestador(db, phone)
    conv_id = _nova_conversa(db, prestador_id, phone, "CONFIRMING")

    ctx = _ctx(
        prestador_id, phone, conv_id=conv_id,
        msg_type=MsgType.BUTTON, button_id=BotaoId.TOMADOR_CORRIGIR,
    )
    confirming_flow(ctx, ConvManager(ctx))

    row = db.select_one("conversations", where={"id": conv_id})
    assert row["status"] == "COLLECTING"


def test_confirming_without_a_button_asks_user_to_use_buttons(db):
    phone = "5511955556666"
    prestador_id = _novo_prestador(db, phone)
    conv_id = _nova_conversa(db, prestador_id, phone, "CONFIRMING")

    ctx = _ctx(prestador_id, phone, text="sim, confirmo", conv_id=conv_id, msg_type=MsgType.TEXT)
    confirming_flow(ctx, ConvManager(ctx))

    row = db.select_one("conversations", where={"id": conv_id})
    assert row["status"] == "CONFIRMING"

    msg = db.select_one("messages", where={"prestador_id": prestador_id})
    assert "bot" in msg["content"].lower() or "botõe" in msg["content"].lower()


def test_collecting_flow_moves_to_confirming_when_data_is_complete(db, monkeypatch):
    phone = "5511977778888"
    prestador_id = _novo_prestador(db, phone)
    conv_id = _nova_conversa(db, prestador_id, phone, "COLLECTING")

    db.insert("iss_rates", data={
        "codigo_municipio": RJ_CODIGO_MUNICIPIO,
        "codigo_tributacao_nacional": "010601",
        "aliquota": 3.0,
        "vigencia_inicio": "2026-01-01",
    })

    fake_client = FakeAIClient(extract_json_responses=[
        {
            "tomador": {"nome": "Cliente LTDA", "cnpj": "11222333000181"},
            "servico": {"descricao": "Consultoria"},
            "valores": {"total": 1500},
        },
        {"value": "010601"},  # classificação do código nacional (checkpoint de ISS)
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_client)
    monkeypatch.setattr(
        collecting_service, "get_cnpj_info",
        lambda cnpj: {"descricao_situacao_cadastral": "ATIVA"},
    )

    ctx = _ctx(prestador_id, phone, text="Cliente LTDA cnpj 11222333000181 consultoria 1500", conv_id=conv_id)
    collecting_flow(ctx, ConvManager(ctx))

    row = db.select_one("conversations", where={"id": conv_id})
    assert row["status"] == "CONFIRMING"

    # _iss_ok() gravou o cTribNac classificado e a alíquota vigente no draft
    draft = json.loads(row["draft_json"])
    assert draft["servico"]["codigo"] == "010601"
    assert draft["valores"]["aliquotaIss"] == 3.0


def test_collecting_flow_rejects_invalid_cnpj_instead_of_advancing(db, monkeypatch):
    """A CNPJ com dígito verificador errado é 'inválido', não 'faltante' — a
    conversa não pode avançar para CONFIRMING com o campo em None."""
    phone = "5511900001111"
    prestador_id = _novo_prestador(db, phone)
    conv_id = _nova_conversa(db, prestador_id, phone, "COLLECTING")

    fake_client = FakeAIClient(extract_json_responses=[
        {
            "tomador": {"nome": "Cliente LTDA", "cnpj": "11222333000180"},  # dígito errado
            "servico": {"descricao": "Consultoria"},
            "valores": {"total": 1500},
        },
    ])
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake_client)

    ctx = _ctx(prestador_id, phone, text="Cliente LTDA cnpj 11222333000180 consultoria 1500", conv_id=conv_id)
    collecting_flow(ctx, ConvManager(ctx))

    row = db.select_one("conversations", where={"id": conv_id})
    assert row["status"] == "COLLECTING"
    assert json.loads(row["draft_json"])["tomador"]["cnpj"] is None


def test_confirming_confirmado_queues_conversation_and_creates_nf(db):
    phone = "5511999990000"
    prestador_id = _novo_prestador(db, phone)
    draft = {
        "tomador": {"nome": "Cliente LTDA", "cnpj": "11222333000181"},
        "servico": {"descricao": "Consultoria", "codigo": "010601"},
        "valores": {"total": 1500, "aliquotaIss": 3.0},
    }
    conv_id = _nova_conversa(db, prestador_id, phone, "CONFIRMING", draft=draft)

    ctx = _ctx(
        prestador_id, phone, conv_id=conv_id,
        msg_type=MsgType.BUTTON, button_id=BotaoId.TOMADOR_CONFIRMADO,
    )
    confirming_flow(ctx, ConvManager(ctx))

    row = db.select_one("conversations", where={"id": conv_id})
    assert row["status"] == "QUEUED"

    nf = db.select_one("nfs", where={"conv_id": conv_id})
    assert nf is not None
    assert nf["cnpj"] == "11222333000181"
    assert nf["codigo_servico"] == "010601"
    assert nf["aliquota_iss"] == 3.0
