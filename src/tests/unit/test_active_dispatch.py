from src.flows.active_flows.active_flow import active_flow  # noqa: F401 (resolves circular import first)
from src.services.active import active_service
from src.types import ContextTomador, ConvStatus, MsgType, TomadorData, User, UserStatus
from src.types.conversation import Conversation


def _ctx(prestador_id: int = 1, phone: str = "5511999999999") -> ContextTomador:
    return ContextTomador(
        user=User(id=prestador_id, phone=phone, status=UserStatus.ACTIVE),
        text="oi", new_data=TomadorData(), db_data=TomadorData(),
        merged=TomadorData(), valid=TomadorData(), msg_type=MsgType.TEXT,
    )


def _conversa(conv_id: int, status: ConvStatus) -> Conversation:
    return Conversation(id=conv_id, prestador_id=1, phone="5511999999999", status=status)


def test_dispatch_routes_to_idle_when_no_active_conversation(monkeypatch):
    calls = []
    monkeypatch.setattr(active_service, "idle_flow", lambda ctx, conv: calls.append("idle"))

    active_service.DispatchActiveService(_ctx()).dispatch(None)

    assert calls == ["idle"]


def test_dispatch_routes_by_conv_status(monkeypatch):
    for status, flow_name in [
        (ConvStatus.COLLECTING, "collecting_flow"),
        (ConvStatus.CONFIRMING, "confirming_flow"),
        (ConvStatus.QUEUED, "queued_flow"),
    ]:
        calls = []
        monkeypatch.setattr(active_service, flow_name, lambda ctx, conv: calls.append(flow_name))

        ctx = _ctx()
        active_service.DispatchActiveService(ctx).dispatch(_conversa(1, status))

        assert calls == [flow_name]
        assert ctx.conv_status == status


def test_dispatch_routes_to_idle_for_unmapped_status(monkeypatch):
    calls = []
    monkeypatch.setattr(active_service, "idle_flow", lambda ctx, conv: calls.append("idle"))

    ctx = _ctx()
    active_service.DispatchActiveService(ctx).dispatch(_conversa(1, ConvStatus.DONE))

    assert calls == ["idle"]
