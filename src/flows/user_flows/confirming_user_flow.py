from src.managers.prestador_manager import PrestadorManager
from src.types import IncomingMessage, UserStatus, ContextPrestador
from src.flows.active_flows.onboarding_flow import criar_project
from src.services.wpp.msg_service import WhatsAppService
from src.services.sign_up.confirming_user_service import ConfirmUserService

def confirming_flow(ctx: ContextPrestador) -> None:
    
    prestador = PrestadorManager(ctx)
    ConfirmUserService(ctx, prestador).dispatch()