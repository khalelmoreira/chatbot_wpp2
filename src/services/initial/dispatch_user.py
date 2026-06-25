from src.types import EstadoUser, User, ContextTomador, DadosPrestador, DadosTomador, ContextPrestador, IncomingMessage
from src.managers.users.user_manager import UserManager
from src.services.shared.msg_service import WhatsAppService
from chatbot_wpp2.src.flows.cadastro_flows.prestador_flow import prestador_flow
from chatbot_wpp2.src.flows.cadastro_flows.endereco_flow import endereco_flow
from src.flows.active_flows import active_flow
from chatbot_wpp2.src.flows.cadastro_flows.endereco_manu_flow import endereco_manu_flow

class DispatchUser:
    def __init__(self, manager: UserManager, user: User, msg: IncomingMessage):
        self.manager = manager
        self.user = user
        self.msg = msg
        self.estado = EstadoUser(self.user.estado)
        self.wpp = WhatsAppService()

    def dispatch(self):

        dispatchers = {
            EstadoUser.NOVO:                     self._new_user,
            EstadoUser.CADASTRO_PRESTADOR:       self._prestador_flow,
            EstadoUser.CADASTRO_ENDERECO:        self._endereco_flow,
            EstadoUser.CADASTRO_ENDERECO_MANUAL: self._endereco_manu_flow,
            EstadoUser.CRIANDO_PROJETO_NOTAAS:   self._notaas_project,
            EstadoUser.ATIVO:                    self._active_flow,
        }

        dispacher = dispatchers.get(self.estado)
        if dispacher is None:
            raise ValueError(f"Estado não mapeado no fluxo: {self.user.estado}")
        return dispacher()
            
    def _new_user(self):
        self.manager.update_state(self.user, EstadoUser.CADASTRO_PRESTADOR)
        self._notf_user("Vamos iniciar seu cadastro...")
        return
    
    def _prestador_flow(self):
        ctx = self._build_ctx(prestador=True)
        return prestador_flow(ctx, self.manager)
    
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