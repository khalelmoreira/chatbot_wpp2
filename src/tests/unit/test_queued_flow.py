from src.flows.active_flows.queued_flow import queued_flow
from src.types import ContextTomador, MsgType, TomadorData, User, UserStatus


def _ctx(prestador_id: int, phone: str) -> ContextTomador:
    return ContextTomador(
        user=User(id=prestador_id, phone=phone, status=UserStatus.ACTIVE),
        text="e ai, sai a nota?", new_data=TomadorData(), db_data=TomadorData(),
        merged=TomadorData(), valid=TomadorData(), msg_type=MsgType.TEXT,
    )


def test_queued_flow_saves_waiting_message(db):
    phone = "5511922223333"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")

    ctx = _ctx(prestador_id, phone)
    queued_flow(ctx, conversation=None)

    msg = db.select_one("messages", where={"prestador_id": prestador_id})
    assert msg is not None
    assert "fila" in msg["content"].lower()
