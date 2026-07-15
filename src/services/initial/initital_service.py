from src.managers.user_manager import UserManager
from src.types import UserStatus, User, ContextTomador, PrestadorData, TomadorData, ContextPrestador, IncomingMessage
from src.services.wpp.msg_service import WhatsAppService
from src.flows.user_flows.idle_user_flow import idle_user_flow
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.confirming_user_flow import confirming_flow
from src.flows.user_flows.address_flow import address_flow
from src.flows.user_flows.project_flow import project_flow
from src.flows.user_flows.certificate_flow import cerfiticate_flow
from src.flows.active_flows import active_flow
from src.utils.build_ctx import build_ctx

class UserResolv:
    def __init__(self, msg: IncomingMessage) -> None:
        self.msg = msg

    def resolv(self) -> tuple[User, bool]:

        manager = UserManager()
        user = manager.get_user(self.msg.phone)

        if user is None:

            user_id: int = manager.criar_user(self.msg)
            user = User(
                id=user_id,
                phone=self.msg.phone,
                name=self.msg.name
            )
            return user, True

        return user, False
    
    def welcome_msg(self) -> None:
        msg = (f"Olá! Seja bem-vindo à automação de notas fiscais.\n\n"
                    "Para começar, me informe:\n"
                    "- Razão social\n- CNPJ\n- E-mail\n- Regime tributário\n- CEP\n- Inscrição municipal")
        #self.wpp.send_msg_text(self.self.msg.phone, self.msg)
        print(f"{msg}\n")

class DispatchUser:
    def __init__(self, user: User, msg: IncomingMessage):
        self.user = user
        self.msg = msg
        self.wpp = WhatsAppService()

    def dispatch(self):

        if self.user.status is None:
            return idle_user_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))

        dispatchers = {
            UserStatus.COLLECTING:  self._collecting_flow,
            UserStatus.CONFIRMING:  self._confirming,
            UserStatus.ADDRESS:     self._address,
            UserStatus.PROJECT:     self._project,
            UserStatus.CERTIFICATE: self._certificate,
            UserStatus.ACTIVE:      self._active,
        }

        dispacher = dispatchers.get(self.user.status)
        if dispacher is None:
            return idle_user_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
        return dispacher()
    
    def _collecting_flow(self):
        return collecting_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _confirming(self):
        return confirming_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _address(self):
        return address_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _project(self):
        return project_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _certificate(self):
        return cerfiticate_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _active(self):
        return active_flow(ctx=build_ctx(ContextTomador, TomadorData, self.user, self.msg))