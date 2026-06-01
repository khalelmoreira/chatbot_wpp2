from rq import Queue
from redis import Redis
from typing import Optional
from config import MAX_TENTATIVAS
from src.repositories.db import executar_modif, fetchone

redis_conn = Redis(host="localhost", port=6379)
fila = Queue(connection=redis_conn)

def busca_reserva_job() -> Optional[dict]:

    return fetchone("""
                    
    UPDATE fila_emissao
    SET status = 'processando'
    WHERE id = (
        SELECT id FROM fila_emissao
        WHERE status = 'pendente'
            AND tentativas < ?
        ORDER BY id ASC
        LIMIT 1
    )
    RETURNING id, payload, tentativas
    """, (MAX_TENTATIVAS,)
    )

def marcar_emitido(job_id: int) -> None:

    executar_modif("""
                   
    UPDATE fila_emissao
    SET status = 'emitido',
        processado_em = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (job_id,)
    )

def marcar_erro(job_id: int, erro: Exception) -> None:

    executar_modif("""
                   
    UPDATE fila_emissao
    SET status = 'pendente',
        erro = ?,
        tentativas = tentativas + 1
    WHERE id = ?
    """, (str(erro), job_id)
    )

def calcular_backoff(tentativas: int) -> int:
    return 15 * (2 ** tentativas)