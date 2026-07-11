from chatbot_wpp2.src.managers.prestador_manager import PrestadorManager
from src.types import IncomingMessage, UserStatus, ContextPrestador
from src.flows.active_flows.onboarding_flow import criar_project
from src.services.wpp.msg_service import WhatsAppService
from chatbot_wpp2.src.services.sign_up.confirming_user_service import ConfirmUserService

def confirming_flow(ctx: ContextPrestador, msg: IncomingMessage, prestador: PrestadorManager) -> None:
    
    ConfirmUserService(ctx, msg, prestador).dispatch()