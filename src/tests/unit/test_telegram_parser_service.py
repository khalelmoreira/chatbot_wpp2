from src.services.telegram import telegram_parser_service as telegram_parser_module
from src.services.telegram.telegram_parser_service import TelegramParser
from src.types import MsgType


def test_parse_retorna_none_sem_message_ou_callback():
    assert TelegramParser({}).parse() is None


def test_parse_mensagem_de_texto():
    payload = {
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {"id": 123456789},
            "from": {"first_name": "Fulano"},
            "text": "oi",
        }
    }

    msg = TelegramParser(payload).parse()

    assert msg is not None
    assert msg.tipo == MsgType.TEXT
    assert msg.phone == "123456789"
    assert msg.msg_id == "1"
    assert msg.timestamp == 1700000000
    assert msg.name == "Fulano"
    assert msg.text == "oi"
    assert msg.channel == "TELEGRAM"


def test_parse_mensagem_sem_from_usa_nome_vazio():
    payload = {
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {"id": 123456789},
            "text": "oi",
        }
    }

    msg = TelegramParser(payload).parse()

    assert msg.name == ""


def test_parse_mensagem_de_voz_transcreve(monkeypatch):
    monkeypatch.setattr(
        telegram_parser_module, "transcrever_audio_telegram", lambda file_id: "texto transcrito"
    )

    payload = {
        "message": {
            "message_id": 2,
            "date": 1700000000,
            "chat": {"id": 123456789},
            "from": {"first_name": "Fulano"},
            "voice": {"file_id": "abc123"},
        }
    }

    msg = TelegramParser(payload).parse()

    assert msg.tipo == MsgType.AUDIO
    assert msg.text == "texto transcrito"


def test_parse_callback_query_vira_botao():
    payload = {
        "callback_query": {
            "id": "cbq1",
            "data": "tomador_confirmado",
            "from": {"first_name": "Fulano"},
            "message": {"date": 1700000000, "chat": {"id": 123456789}},
        }
    }

    msg = TelegramParser(payload).parse()

    assert msg.tipo == MsgType.BUTTON
    assert msg.button_id == "tomador_confirmado"
    assert msg.phone == "123456789"
    assert msg.text == ""


def test_parse_callback_query_sem_chat_retorna_none():
    payload = {"callback_query": {"id": "cbq1", "data": "x", "message": {}}}

    assert TelegramParser(payload).parse() is None


def test_parse_tipo_de_mensagem_nao_tratado_retorna_none():
    payload = {
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {"id": 123456789},
            "sticker": {"file_id": "xyz"},
        }
    }

    assert TelegramParser(payload).parse() is None
