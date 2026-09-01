from src.managers.msg_manager import MsgManager
from src.types import Role, User


def _user(db, phone: str = "5511900000000") -> User:
    uid = db.insert("prestador", data={"phone": phone}, returning="id")
    return User(id=uid, phone=phone)


def test_get_msg_history_returns_most_recent_in_chronological_order(db):
    user = _user(db)
    mgr = MsgManager(user)
    for i in range(1, 16):
        mgr.save_msg(Role.USER if i % 2 else Role.AI, f"m{i}")

    hist = mgr.get_msg_history(limite=5)

    assert [r["content"] for r in hist] == ["m11", "m12", "m13", "m14", "m15"]


def test_get_ai_history_excludes_the_just_saved_inbound_message(db):
    user = _user(db)
    mgr = MsgManager(user)
    mgr.save_msg(Role.USER, "oi")
    mgr.save_msg(Role.AI, "quer começar seu cadastro?")
    mgr.save_msg(Role.USER, "sim")  # the current inbound, already persisted

    hist = mgr.get_ai_history()

    assert hist == [
        {"role": "user", "content": "oi"},
        {"role": "ai", "content": "quer começar seu cadastro?"},
    ]
