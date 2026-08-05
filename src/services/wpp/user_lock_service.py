import threading
from contextlib import contextmanager
from typing import Iterator

# MVP guard against concurrent messages from the same phone racing on
# read-modify-write DB calls (e.g. draft_json). In-memory only: fine for a
# single process, wouldn't hold across multiple app instances.

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()

def _get_lock(phone: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(phone, threading.Lock())

@contextmanager
def with_user_lock(phone: str) -> Iterator[None]:
    lock = _get_lock(phone)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
