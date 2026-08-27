from src.handlers import telegram_handler as telegram_handler_module
from src.handlers.telegram_handler import telegram_handler
from src.types import BotaoId


def _button_payload(callback_id: str, phone: str = "123456789"):
    return {
        "callback_query": {
            "id": callback_id,
            "data": BotaoId.TOMADOR_CONFIRMADO.value,
            "from": {"first_name": "Fulano"},
            "message": {"date": 1748185200, "chat": {"id": int(phone)}},
        }
    }


def test_duplicate_webhook_delivery_processed_once(db, monkeypatch):
    calls = []
    monkeypatch.setattr(telegram_handler_module, "initial_handler", lambda msg: calls.append(msg))

    payload = _button_payload("cbq-dup-1")
    telegram_handler(payload)
    telegram_handler(payload)

    assert len(calls) == 1


def test_unhandled_exception_notifies_user_instead_of_crashing(db):
    phone = "123456789"
    prestador_id = db.insert(
        "prestador", data={"phone": phone, "status": "ACTIVE", "channel": "TELEGRAM"}, returning="id"
    )

    payload = {
        "callback_query": {
            "id": "cbq-botao-invalido",
            "data": "botao_que_nao_existe",
            "from": {"first_name": "Fulano"},
            "message": {"date": 1748185200, "chat": {"id": int(phone)}},
        }
    }
    db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "CONFIRMING", "draft_json": "{}"},
    )

    telegram_handler(payload)  # não deve levantar

    msgs = db.select("messages", where={"prestador_id": prestador_id})
    assert any("problema" in m["content"].lower() or "tente" in m["content"].lower() for m in msgs)
