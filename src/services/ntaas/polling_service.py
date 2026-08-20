import logging
import os

from dotenv import load_dotenv

from src.managers.nfs.nf_polling_manager import NfsPollingManager
from src.services.ntaas.req_status import req_status_notaas
from src.types import NfseStatus

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
            result = req_status_notaas(manager.job["invoice_id"], os.getenv("NOTAAS_API_KEY"))
            logger.debug("resultado consulta job %s: %s", manager.job_id, result)

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