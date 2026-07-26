import logging
import os
from src.managers.nfs.nf_polling_manager import NfsPollingManager
from src.types import NfseStatus
from dotenv import load_dotenv
from src.services.notaas.req_status import req_status_notaas

logger = logging.getLogger(__name__)
load_dotenv()

def match_jobs_processing() -> None:
    """
    Busca jobs com status=processing e invoice_id preenchido,
    consulta status na Notaas, resolve estado final.
    """

    jobs = NfsPollingManager.get_jobs()

    for manager in jobs:
        try:
            print(f"\n\n----------------TESTE POLLING----------------\n\n")
            result = req_status_notaas(manager.job["invoice_id"], os.getenv("NOTAAS_API_KEY"))
            print(f"RESULTADO CONSULTA: {result}")

        except Exception:
            logger.exception("erro ao consultar status do job %s", manager.job_id)
            continue

        status = result["status"]
        if status == NfseStatus.ISSUED:
            manager.marcar_issued(result)

        elif status == NfseStatus.ERROR:
            manager.marcar_erro(result.get("errorMessage", ""))
        
        elif status == NfseStatus.CANCELLED:
            manager.marcar_cancelled()