import pytest

from src.services.wpp import wpp_parser_service as wpp_parser_module
from src.services.wpp.wpp_parser_service import WppParser
from src.types import MsgType


def _payload(value: dict) -> dict:
    return {"entry": [{"changes": [{"value": value}]}]}


def _message(**overrides) -> dict:
    base = {"from": "5511999999999", "id": "wamid.1", "timestamp": "1700000000", "type": "text"}
    base.update(overrides)
    return base


def test_parse_retorna_none_sem_mensagens():
    assert WppParser(_payload({"messages": []})).parse() is None


def test_parse_levanta_value_error_para_payload_malformado():
    with pytest.raises(ValueError):
        WppParser({"entry": []}).parse()


def test_parse_mensagem_de_texto():
    payload = _payload({
        "contacts": [{"profile": {"name": "Fulano"}}],
        "messages": [_message(type="text", text={"body": "oi"})],
    })

    msg = WppParser(payload).parse()

    assert msg is not None
    assert msg.tipo == MsgType.TEXT
    assert msg.phone == "5511999999999"
    assert msg.msg_id == "wamid.1"
    assert msg.timestamp == 1700000000
    assert msg.name == "Fulano"
    assert msg.text == "oi"


def test_parse_mensagem_de_texto_sem_contato_usa_nome_vazio():
    payload = _payload({"messages": [_message(type="text", text={"body": "oi"})]})

    msg = WppParser(payload).parse()

    assert msg.name == ""


def test_parse_mensagem_de_audio_transcreve(monkeypatch):
    monkeypatch.setattr(wpp_parser_module, "transcrever_audio_wpp", lambda msg_id: "texto transcrito")

    payload = _payload({"messages": [_message(type="audio")]})
    msg = WppParser(payload).parse()

    assert msg.tipo == MsgType.AUDIO
    assert msg.text == "texto transcrito"


def test_parse_botao_interativo():
    payload = _payload({
        "messages": [_message(
            type="interactive",
            interactive={"type": "button_reply", "button_reply": {"id": "tomador_confirmado"}},
        )],
    })

    msg = WppParser(payload).parse()

    assert msg.tipo == MsgType.BUTTON
    assert msg.button_id == "tomador_confirmado"
    assert msg.text == ""


def test_parse_subtipo_interativo_nao_tratado_retorna_none():
    payload = _payload({
        "messages": [_message(type="interactive", interactive={"type": "list_reply"})],
    })

    assert WppParser(payload).parse() is None


def test_parse_tipo_de_mensagem_nao_tratado_retorna_none():
    payload = _payload({"messages": [_message(type="sticker")]})

    assert WppParser(payload).parse() is None
