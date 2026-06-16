from src.managers.user_manager import UserManager
from src.types.incoming_msg import IncomingMessage
from src.services.initial.dispatch_state import dispatch_state
from src.services.initial.user_exists import user_exists
from src.utils.debug import print_table

def fluxo_principal(msg: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO PRINCIPAL----------------\n\n")

    user_manager = UserManager()
    user = user_exists(msg, user_manager)
    dispatch_state(user_manager, user, msg)