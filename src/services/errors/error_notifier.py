"""Notifica o usuário quando uma falha acontece fora do ciclo normal de
requisição/resposta do WhatsApp — ex.: o EmissaoWorker processa jobs em uma
thread própria, sem um ContextTomador disponível para usar MsgManager/ConvManager
diretamente. As funções aqui montam o mínimo necessário (prestador_id, phone,
conv_id) a partir do que o chamador já tem à mão."""

import logging

from src.database.db import DB
from src.services.wpp.msg_service import WhatsAppService
from src.types import AIClientError, NtassOrgError, Role

logger = logging.getLogger(__name__)

MSG_IA_INDISPONIVEL = (
    "🤖 Não consegui entender sua mensagem agora — nosso serviço de IA está "
    "instável. Pode tentar de novo em alguns minutos?"
)
MSG_NOTAAS_INDISPONIVEL = (
    "⚠️ Não consegui falar com a Notaas agora para seguir com seu cadastro/nota. "
    "Tente novamente em alguns minutos."
)
MSG_GENERICA = (
    "⚠️ Tive um problema para processar sua mensagem agora. Pode tentar de novo?"
)


def mensagem_para_erro(exc: Exception) -> str:
    """Mapeia exceções conhecidas para uma mensagem de usuário específica —
    além de "algo deu errado", cada família de falha (IA fora do ar, Notaas
    fora do ar) recebe uma explicação curta do que houve, sem detalhe técnico."""

    if isinstance(exc, AIClientError):
        return MSG_IA_INDISPONIVEL
    if isinstance(exc, NtassOrgError):
        return MSG_NOTAAS_INDISPONIVEL
    return MSG_GENERICA


def notificar_erro_processamento(prestador_id: int | None, phone: str, exc: Exception) -> None:
    """Boundary de erro chamado pelo handler do webhook do WhatsApp: qualquer
    exceção não tratada que escape do dispatch de fluxos cai aqui em vez de
    silenciar (thread do debounce) ou virar 500 sem contexto (mensagem BUTTON
    síncrona) — o usuário sempre recebe alguma resposta."""

    logger.exception("erro ao processar mensagem de %s", phone)
    if prestador_id is None:
        logger.warning("phone=%s sem prestador cadastrado, não foi possível notificar", phone)
        return
    _salvar_e_enviar(prestador_id, phone, mensagem_para_erro(exc))


def notificar_falha_emissao(manager, msg: str) -> None:
    """`manager` é um NfsWorkerManager — aceito duck-typed para não criar
    dependência circular entre `services.errors` e `managers.nfs`."""

    destino = manager.get_prestador_id_e_phone()
    if destino is None:
        logger.warning("conv_id=%s sem prestador/phone associado, não foi possível notificar", manager.cid)
        return

    _salvar_e_enviar(destino["prestador_id"], destino["phone"], msg)

    DB().update(
        "conversations",
        data={"status": "ERROR", "updated_at": "CURRENT_TIMESTAMP"},
        where={"id": manager.cid},
    )


def notificar_erro_generico(prestador_id: int, phone: str, msg: str) -> None:
    _salvar_e_enviar(prestador_id, phone, msg)


def _salvar_e_enviar(prestador_id: int, phone: str, msg: str) -> None:
    DB().insert(
        "messages",
        data={
            "prestador_id": prestador_id,
            "phone": phone,
            "role": Role.AI,
            "content": msg,
        },
    )
    wpp = WhatsAppService()
    # wpp.send_msg_text(phone, msg)
    print(f"{msg}\n")
