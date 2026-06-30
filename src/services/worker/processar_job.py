import logging
from config import MAX_TENTATIVAS
from src.managers.nfs.nf_worker_manager import NfsWorkerManager
from src.services.notaas.emission_service import emitir_nf
from src.services.worker.fila_service import calcular_backoff

logger = logging.getLogger(__name__)

def processar_job(manager: NfsWorkerManager) -> float | None:
    """
    Processa um único job. Retorna quantos segundos o worker deve
    esperar antes do próximo poll (None = usar intervalo padrão).
    """

    job_id = manager.job_id
    job    = manager.job

    manager.resetar_jobs_travados()
    print(f"JOB: {job}\n") if job is None else print(f"JOB: {dict(job)}\n")

    payload  = {
        "tomador": {"nome": job["nome"], "cnpj": job["cnpj"]},
        "servico": {"descricao": job["descricao_servico"]},
        "valores": {"total": job["valor_total"], "aliquotaIss": job["aliquota_iss"]},
    }

    try:
        response = emitir_nf(payload)
        manager.save_invoice_id(response["invoiceId"])
        logger.info("job %s emitido com sucesso", job_id)
        return 10.0
    
    except Exception as e:
        manager.marcar_erro(job_id, str(e))
        espera = calcular_backoff(job["tentativas"])

        logger.info(
            "job %s falhou (tentativa %s/%s): %s",
            job_id, job["tentativas"], MAX_TENTATIVAS, e,
            )
        return espera