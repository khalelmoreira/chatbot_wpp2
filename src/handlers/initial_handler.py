from src.services.initial.initital_service import DispatchUser, UserResolv
from src.types import IncomingMessage


def initial_handler(msg: IncomingMessage):

    print("\n\n----------------INITIAL HANDLER----------------\n\n")

    user, is_new = UserResolv(msg).resolv()
    if is_new:
        UserResolv(msg).welcome_msg()

    DispatchUser(user, msg).dispatch()
