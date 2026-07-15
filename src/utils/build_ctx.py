from typing import TypeVar
from src.types import IncomingMessage, User, ContextBase

T = TypeVar("T")
C = TypeVar("C", bound=ContextBase)

def build_ctx(ctx_cls: type[C], data_cls: type[T], user: User, msg: IncomingMessage, **extra) -> C:
    return ctx_cls(
        user=user,
        text=msg.text,
        new_data=data_cls(),
        db_data=data_cls(),
        merged=data_cls(),
        validated=data_cls(),
        msg_type=msg.tipo,
        button_id=msg.button_id,
        **extra,
    )