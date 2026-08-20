import threading
import time

from src.services.wpp.user_lock_service import with_user_lock


def test_with_user_lock_serializes_same_phone():
    """Duas mensagens simultâneas do mesmo telefone não podem interlear leituras
    e escritas de draft_json — sem o lock, um read-modify-write concorrente
    (ex.: extração de duas mensagens em paralelo) pode perder uma das duas."""

    shared = {"counter": 0}
    resultados = []

    def _incrementa():
        with with_user_lock("5521991112222"):
            valor = shared["counter"]
            time.sleep(0.01)  # força a janela de corrida se o lock não existisse
            shared["counter"] = valor + 1
            resultados.append(shared["counter"])

    threads = [threading.Thread(target=_incrementa) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert shared["counter"] == 10
    assert sorted(resultados) == list(range(1, 11))


def test_with_user_lock_does_not_block_different_phones():
    order = []

    def _hold(phone: str, delay: float):
        with with_user_lock(phone):
            time.sleep(delay)
            order.append(phone)

    t1 = threading.Thread(target=_hold, args=("phone-a", 0.05))
    t2 = threading.Thread(target=_hold, args=("phone-b", 0.0))
    t1.start()
    time.sleep(0.01)
    t2.start()
    t1.join()
    t2.join()

    # phone-b não fica preso esperando phone-a liberar o lock
    assert order[0] == "phone-b"
