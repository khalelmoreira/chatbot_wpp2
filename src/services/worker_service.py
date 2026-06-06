import time
import json
import threading
import logging
from config import MAX_TENTATIVAS
from src.repositories.message_repo import limpar_msg_antigas
from src.services.fila_service import calcular_backoff
from src.repositories.fila_emissao_repo import FilaManager
from src.services.nfse_service import emitir_nf
from src.utils.logger import logger

def worker_emissao() -> None:

    logger.info("Worker de emissao iniciado")

    while True:

        fila = FilaManager()

        job = fila.get_reserva_job()

        if not job:
            time.sleep(2)
            continue

        job_id = job["id"]
        tentativas = job["tentativas"]

        try:
            payload = json.loads(job["payload"])
            emitir_nf(payload)
            fila.marcar_emitido(job_id)

            logger.info(f"job {job_id} emitido com sucesso")

            time.sleep(10)

        except Exception as e:

            fila.marcar_erro(job_id, e)
            espera = calcular_backoff(tentativas)

            logger.info(f"job {job_id} falhou (tentativa {tentativas + 1}/{MAX_TENTATIVAS}): {e}")
            logger.info(f"aguardando {espera}s antes de tentar proximo job")

            time.sleep(espera)

def worker_limpeza_msg():

    print(f"worker limpeza iniciado\n")

    while True:
        try:
            limpar_msg_antigas()
        except Exception as e:
            print(f"[ERRO LIMPEZA MENSAGENS DB] {e}")

        time.sleep(3600)

def start_workers() -> None:

    threading.Thread(
        target=worker_emissao,
        daemon=True,
        name="worker-emissao"
    ).start()

    threading.Thread(
        target=worker_limpeza_msg,
        daemon=True,
        name="worker-limpeza-msg"
    ).start()