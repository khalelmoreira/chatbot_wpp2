import logging

from src.managers.msg_manager import MsgManager
from src.services.initial.initital_service import DispatchUser, UserResolv
from src.types import IncomingMessage, Role
from src.utils.debug import log_table

logger = logging.getLogger(__name__)

def initial_handler(msg: IncomingMessage):

    logger.debug("initial_handler: phone=%s", msg.phone)

    user, _ = UserResolv(msg).resolv()

    # Persiste a mensagem recebida uma única vez, antes de qualquer flow, para
    # todos os caminhos (onboarding e emissão). Cliques de botão chegam com text
    # vazio — registra o id do botão para o histórico não ter linhas em branco.
    content = msg.text or msg.button_id or ""
    if content:
        MsgManager(user).save_msg(role=Role.USER, content=content)
        log_table(table_name="messages", where="phone = ?", params=(msg.phone,))

    DispatchUser(user, msg).dispatch()
