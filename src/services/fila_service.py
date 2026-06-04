from rq import Queue
from redis import Redis

redis_conn = Redis(host="localhost", port=6379)
fila = Queue(connection=redis_conn)

def calcular_backoff(tentativas: int) -> int:
    return 15 * (2 ** tentativas)