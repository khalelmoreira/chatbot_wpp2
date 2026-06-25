from src.managers.users.user_manager import UserManager
from src.types import IncomingMessage
from chatbot_wpp2.src.services.initial.dispatch_user import DispatchUser
from src.services.initial.user_exists import user_exists
from src.utils.debug import print_table

def initial_flow(msg: IncomingMessage):

    print(f"\n\n----------------INITIAL FLOW----------------\n\n")

    user_manager = UserManager(msg.phone)
    user = user_exists(msg, user_manager)
    dispatch = DispatchUser(user_manager, user, msg)
    dispatch.dispatch()