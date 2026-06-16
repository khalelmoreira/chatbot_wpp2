import time
import json
import threading
import logging
from config import MAX_TENTATIVAS
from chatbot_wpp2.src.services.worker.fila_service import calcular_backoff
from chatbot_wpp2.src.managers.nfse_worker_manager import NfsWorkerManager
from chatbot_wpp2.src.services.shared.emission_service import emitir_nf
from src.utils.logger import logger

def worker_emissao() -> None:

    logger.info("Worker de emissao iniciado")

    while True:
        
        print(f"\n\n----------------TESTE WORKER EMISSAO----------------\n\n")

        manager = NfsWorkerManager()
        manager.resetar_jobs_travados()
        job = manager.get_reserva_job()
        print(f"JOB: {job}\n") if job is None else print(f"JOB: {dict(job)}\n")

        if not job:
            time.sleep(10)
            continue

        job_id     = job["id"]
        tentativas = job["tentativas"]

        try:
            payload  = json.loads(job["payload_enviado"])
            response = emitir_nf(payload)

            invoice_id = response["invoiceId"]
            manager.save_invoice_id(job_id, invoice_id)

            logger.info(f"job {job_id} emitido com sucesso")
            time.sleep(10)

        except Exception as e:
            manager.marcar_erro(job_id, e)
            espera = calcular_backoff(tentativas)

            logger.info(f"job {job_id} falhou (tentativa {tentativas}/{MAX_TENTATIVAS}): {e}")
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