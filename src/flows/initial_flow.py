from src.managers.user_manager import UserManager
from src.types import IncomingMessage
from src.services.initial.dispatch_state import dispatch_state
from src.services.initial.user_exists import user_exists
from src.utils.debug import print_table

def initial_flow(msg: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO PRINCIPAL----------------\n\n")

    user_manager = UserManager(msg.phone)
    user = user_exists(msg, user_manager)
    dispatch_state(user_manager, user, msg)