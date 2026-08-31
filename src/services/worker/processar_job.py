import logging

from config import MAX_TENTATIVAS
from src.managers.nfs.nf_worker_manager import NfsWorkerManager
from src.services.errors.error_notifier import notificar_falha_emissao
from src.services.ntaas.emission_service import emitir_nf
from src.services.worker.fila_service import calcular_backoff
from src.types import NotaasEmissaoPermanenteError, NotaasEmissaoTransitoriaError

logger = logging.getLogger(__name__)

MSG_FALHA_PERMANENTE = (
    "❌ Não consegui emitir sua nota fiscal: a Notaas rejeitou os dados enviados "
    "(possivelmente CNPJ do tomador, cidade não suportada ou outro campo inválido). "
    "Corrija os dados enviando uma nova mensagem para tentar de novo."
)
MSG_FALHA_TRANSITORIA_ESGOTADA = (
    "❌ Não consegui emitir sua nota fiscal após várias tentativas — a Notaas "
    "está indisponível no momento. Envie uma nova mensagem para tentar novamente "
    "mais tarde."
)

def processar_job(manager: NfsWorkerManager) -> float | None:
    """
    Processa um único job. Retorna quantos segundos o worker deve
    esperar antes do próximo poll (None = usar intervalo padrão).
    """

    job_id = manager.jid
    job    = manager.job

    logger.debug("job=%s", job)

    servico = {"descricao": job.descricao_servico}
    if job.codigo_servico:
        servico["codigo"] = job.codigo_servico

    payload  = {
        "tomador": {"nome": job.nome, "cnpj": job.cnpj},
        "servico": servico,
        "valores": {"total": job.valor_total, "aliquotaIss": job.aliquota_iss},
    }

    try:
        response = emitir_nf(payload)
        manager.save_invoice_id(response["invoiceId"])
        logger.info("job %s emitido com sucesso", job_id)
        return 10.0

    except NotaasEmissaoPermanenteError as e:
        manager.marcar_erro_permanente(str(e))
        notificar_falha_emissao(manager, MSG_FALHA_PERMANENTE)
        logger.error("job %s rejeitado permanentemente pela Notaas: %s", job_id, e)
        return None

    except NotaasEmissaoTransitoriaError as e:
        manager.marcar_erro(job.tentativas, str(e))
        if job.tentativas >= MAX_TENTATIVAS:
            notificar_falha_emissao(manager, MSG_FALHA_TRANSITORIA_ESGOTADA)
        espera = calcular_backoff(job.tentativas)
        logger.info(
            "job %s falhou de forma transitoria (tentativa %s/%s): %s",
            job_id, job.tentativas, MAX_TENTATIVAS, e,
        )
        return espera

    except Exception as e:
        manager.marcar_erro(job.tentativas, str(e))
        if job.tentativas >= MAX_TENTATIVAS:
            notificar_falha_emissao(manager, MSG_FALHA_TRANSITORIA_ESGOTADA)
        espera = calcular_backoff(job.tentativas)

        logger.exception(
            "job %s falhou com erro inesperado (tentativa %s/%s): %s",
            job_id, job.tentativas, MAX_TENTATIVAS, e,
        )
        return espera