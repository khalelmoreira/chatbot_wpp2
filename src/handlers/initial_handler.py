import logging

from src.services.initial.initital_service import DispatchUser, UserResolv
from src.types import IncomingMessage

logger = logging.getLogger(__name__)

def initial_handler(msg: IncomingMessage):

    logger.debug("initial_handler: phone=%s", msg.phone)

    user, _ = UserResolv(msg).resolv()

    DispatchUser(user, msg).dispatch()
