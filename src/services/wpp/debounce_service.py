import threading
from typing import Callable
from src.types import IncomingMessage, MsgType

# MVP fix for bursts of messages from the same user (e.g. "oi", "quero
# emitir nota", "valor 500" sent as separate bubbles): buffer TEXT/AUDIO
# messages per phone and flush them as one merged message after a quiet
# window, instead of running extraction once per bubble. BUTTON messages
# are deterministic actions, not part of a burst, so they flush whatever
# is pending and are processed immediately, preserving arrival order.

DEBOUNCE_SECONDS = 4.0

_buffers: dict[str, list[IncomingMessage]] = {}
_timers: dict[str, threading.Timer] = {}
_guard = threading.Lock()

def buffer_message(msg: IncomingMessage, on_flush: Callable[[IncomingMessage], None]) -> None:
    if msg.tipo == MsgType.BUTTON:
        _flush(msg.phone, on_flush)
        on_flush(msg)
        return

    with _guard:
        _buffers.setdefault(msg.phone, []).append(msg)

        pending_timer = _timers.get(msg.phone)
        if pending_timer is not None:
            pending_timer.cancel()

        timer = threading.Timer(DEBOUNCE_SECONDS, _flush, args=(msg.phone, on_flush))
        timer.daemon = True
        _timers[msg.phone] = timer
        timer.start()

def _flush(phone: str, on_flush: Callable[[IncomingMessage], None]) -> None:
    with _guard:
        pending = _buffers.pop(phone, [])
        _timers.pop(phone, None)

    if not pending:
        return

    on_flush(_merge(pending))

def _merge(messages: list[IncomingMessage]) -> IncomingMessage:
    last = messages[-1]
    combined_text = "\n".join(m.text for m in messages if m.text)

    return IncomingMessage(
        msg_id=last.msg_id,
        phone=last.phone,
        name=last.name,
        tipo=last.tipo,
        timestamp=last.timestamp,
        text=combined_text,
        button_id=last.button_id,
    )
