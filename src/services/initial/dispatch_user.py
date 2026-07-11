from src.types import UserStatus, User, ContextTomador, DadosPrestador, DadosTomador, ContextPrestador, IncomingMessage
from chatbot_wpp2.src.managers.user_manager import UserManager
from src.services.wpp.msg_service import WhatsAppService
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.confirming_user_flow import confirming_flow
from src.flows.user_flows.address_flow import address_flow
from chatbot_wpp2.src.flows.user_flows.project_service import project_flow
from src.flows.user_flows.idle_user_flow import idle_user_flow
from src.flows.active_flows import active_flow

class DispatchUser:
    def __init__(self, manager: UserManager, user: User, msg: IncomingMessage):
        self.manager = manager
        self.user = user
        self.msg = msg
        self.wpp = WhatsAppService()

    def dispatch(self):

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
            return idle_user_flow(ctx=self._build_ctx(prestador=True))
        return dispacher()
    
    def _collecting_flow(self):
        ctx = self._build_ctx(prestador=True)
        return collecting_flow(ctx, self.manager)
    
    def _confirming(self):
        ctx = self._build_ctx(prestador=True)
        return confirming_flow(ctx, self.msg, manager)
    
    def _address(self):
        ctx = self._build_ctx(prestador=True)
        return address_flow(ctx, self.msg, manager)
    
    def _project(self):
        ctx = self._build_ctx(prestador=True)
        return project_flow(ctx, self.msg, manager)
    
    def _certificate(self):
        return 
    
    def _active(self):
        ctx = self._build_ctx(tomador=True)
        return active_flow(ctx, self.msg)

    def _build_ctx(self, prestador: bool = False, tomador: bool = False):
        if prestador:
            return ContextPrestador(
                user=self.user,
                text=self.msg.text,
                dados_novos=DadosPrestador(),
                dados_db=DadosPrestador(),
                dados_completos=DadosPrestador(),
            )
        if tomador:
            return ContextTomador(
                user=self.user,
                text=self.msg.text,
                dados_novos=DadosTomador(),
                dados_db=DadosTomador(),
                dados_completos=DadosTomador(),
            )
        else:
            return None
        
    def _notf_user(self, msg: str) -> None:
        #self.wpp.send_msg_text(self.msg.phone, msg)
        print(f"{msg}\n")