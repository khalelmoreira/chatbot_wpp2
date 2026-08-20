import logging

from src.services.initial.initital_service import DispatchUser, UserResolv
from src.types import IncomingMessage

logger = logging.getLogger(__name__)

def initial_handler(msg: IncomingMessage):

    logger.debug("initial_handler: phone=%s", msg.phone)

    user, is_new = UserResolv(msg).resolv()
    if is_new:
        UserResolv(msg).welcome_msg()

    DispatchUser(user, msg).dispatch()
