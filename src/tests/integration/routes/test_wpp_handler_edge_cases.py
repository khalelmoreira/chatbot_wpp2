from src.handlers import wpp_handler as wpp_handler_module
from src.handlers.wpp_handler import wpp_handler
from src.types import BotaoId


def _button_payload(msg_id: str, phone: str = "5521991112222"):
    return {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "id": msg_id,
                        "timestamp": "1748185200",
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": BotaoId.TOMADOR_CONFIRMADO.value, "title": "Confirmar"},
                        },
                    }],
                    "contacts": [{"profile": {"name": "Fulano"}}],
                }
            }]
        }]
    }


def test_duplicate_webhook_delivery_processed_once(db, monkeypatch):
    calls = []
    monkeypatch.setattr(wpp_handler_module, "initial_handler", lambda msg: calls.append(msg))

    payload = _button_payload("wamid.dup-1")
    wpp_handler(payload)
    wpp_handler(payload)

    assert len(calls) == 1


def test_unhandled_exception_notifies_user_instead_of_crashing(db):
    phone = "5521991112222"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")

    # botão desconhecido força o ValueError em ConfirmingService.dispatch — o
    # boundary de erro do handler deve virar uma mensagem pro usuário em vez
    # de propagar e derrubar a requisição.
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "id": "wamid.botao-invalido",
                        "timestamp": "1748185200",
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": "botao_que_nao_existe", "title": "???"},
                        },
                    }],
                    "contacts": [{"profile": {"name": "Fulano"}}],
                }
            }]
        }]
    }
    db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "CONFIRMING", "draft_json": "{}"},
    )

    wpp_handler(payload)  # não deve levantar

    msgs = db.select("messages", where={"prestador_id": prestador_id})
    assert any("problema" in m["content"].lower() or "tente" in m["content"].lower() for m in msgs)
