from chatbot_wpp2.src.managers.user_manager import UserManager
from src.types import IncomingMessage
from chatbot_wpp2.src.services.initial.initital_service import InitialService, DispatchUser
from src.utils.debug import print_table

def initial_flow(msg: IncomingMessage):

    print(f"\n\n----------------INITIAL FLOW----------------\n\n")

    user = InitialService(msg).user_exists()
    DispatchUser(user, msg).dispatch()