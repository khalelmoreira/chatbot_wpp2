from src.types import IncomingMessage
from src.services.initial.initital_service import DispatchUser, UserResolv

def initial_flow(msg: IncomingMessage):

    print(f"\n\n----------------INITIAL FLOW----------------\n\n")

    user, is_new = UserResolv(msg).resolv()
    if is_new:
        UserResolv(msg).welcome_msg()

    DispatchUser(user, msg).dispatch()
