"""Idle flow with conversation history: a bare "sim" right after the bot offered
to start the cadastro must classify as ONBOARDING and move the user to COLLECTING,
not loop back to the greeting. Regression for the sign-up live-test loop."""

from src.flows.user_flows.idle_user_flow import idle_user_flow
from src.managers.msg_manager import MsgManager
from src.services.ai import ai_client_factory
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import ContextPrestador, MsgType, PrestadorData, Role, User


def _ctx(user: User, text: str) -> ContextPrestador:
    return ContextPrestador(
        user=user, text=text,
        new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=PrestadorData(), msg_type=MsgType.TEXT,
    )


def test_sim_after_greeting_advances_to_collecting(db, monkeypatch):
    phone = "5511900007777"
    uid = db.insert("prestador", data={"phone": phone}, returning="id")
    user = User(id=uid, phone=phone, status=None)

    mgr = MsgManager(user)
    mgr.save_msg(Role.USER, "oi")
    mgr.save_msg(Role.AI, "Olá! Eu crio o cadastro da sua empresa. Quer começar?")
    mgr.save_msg(Role.USER, "sim")  # current inbound, persisted by initial_handler

    fake = FakeAIClient(
        extract_json_responses=[{"value": "ONBOARDING"}, {}],  # classify, then collecting extract
        extract_text_response="Boa! Me envie nome da empresa, CNPJ, CEP, e-mail e regime.",
    )
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: fake)

    idle_user_flow(_ctx(user, text="sim"))

    assert db.select_one("prestador", where={"id": uid})["status"] == "COLLECTING"

    # the intent classification saw the prior turns, current message dropped
    assert fake.histories[0] == [
        {"role": "user", "content": "oi"},
        {"role": "ai", "content": "Olá! Eu crio o cadastro da sua empresa. Quer começar?"},
    ]
