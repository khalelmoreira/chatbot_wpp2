from src.types import UserStatus, User, ContextTomador, DadosPrestador, DadosTomador, ContextPrestador, IncomingMessage
from chatbot_wpp2.src.managers.user_manager import UserManager
from src.services.wpp.msg_service import WhatsAppService
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.cadastro_flows.endereco_flow import endereco_flow
from src.flows.active_flows import active_flow
from src.flows.cadastro_flows.endereco_manu_flow import endereco_manu_flow

class DispatchUser:
    def __init__(self, manager: UserManager, user: User, msg: IncomingMessage):
        self.manager = manager
        self.user = user
        self.msg = msg
        self.wpp = WhatsAppService()

    def dispatch(self, status: UserStatus | None = None):

        if not status:
            estado = UserStatus(self.user.estado)
        else:
            estado = UserStatus(status)

        dispatchers = {
            UserStatus.NEW:        self._new_user,
            UserStatus.COLLECTING: self._collecting_flow,
            UserStatus.NO_ADDRESS: self._endereco_flow,
            UserStatus.CONFIRMING: self._endereco_manu_flow,
            UserStatus.QUEUED:     self._notaas_project,
            UserStatus.ATIVO:      self._active_flow,
        }

        dispacher = dispatchers.get(estado)
        if dispacher is None:
            raise ValueError(f"Estado não mapeado no fluxo: {estado}")
        return dispacher()
            
    def _new_user(self):
        self.manager.update_state(self.user, UserStatus.COLLECTING)
        self._notf_user("Vamos iniciar seu cadastro...")
        return
    
    def _collecting_flow(self):
        ctx = self._build_ctx(prestador=True)
        return collecting_flow(ctx, self.manager)
    
    def _endereco_flow(self):
        return endereco_flow(self.msg, self.manager)
    
    def _endereco_manu_flow(self):
        return endereco_manu_flow(self.msg, self.manager)
    
    def _notaas_project(self):
        self._notf_user("Ainda estamos configurando sua conta, aguarde um momento.")
        return
    
    def _active_flow(self):
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