from chatbot_wpp2.src.managers.user_manager import UserManager
from src.types import UserStatus, User, ContextTomador, PrestadorData, TomadorData, ContextPrestador, IncomingMessage
from src.services.wpp.msg_service import WhatsAppService
from src.flows.user_flows.idle_user_flow import idle_user_flow
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.confirming_user_flow import confirming_flow
from src.flows.user_flows.address_flow import address_flow
from chatbot_wpp2.src.flows.user_flows.project_flow import project_flow
from src.flows.user_flows.certificate_flow import cerfiticate_flow
from src.flows.active_flows import active_flow


def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.self.msg.phone, self.msg)
    print(f"{msg}\n")

class InitialService:
    def __init__(self, msg: IncomingMessage):
        self.msg = msg

    def user_exists(self) -> User:

        user = UserManager()
        row = user.get_user(self.msg.phone)

        if not row[0]["phone"]:
            
            user_id = user.criar_user(self.msg)

            notf_user(f"Olá! Seja bem-vindo à automação de notas fiscais.\n\n"
                "Para começar, me informe:\n"
                "- Razão social\n- CNPJ\n- E-mail\n- Regime tributário\n- CEP\n- Inscrição municipal")
            
            return User(
                id=user_id,
                phone=self.msg.phone,
                name=self.msg.name
            )
        
        status = dict(row[0]["status"])
        return User(
            id=row[0]["id"],
            phone=self.msg.phone,
            name=self.msg.name,
            status=UserStatus(status.get(status))
        )
    
class DispatchUser:
    def __init__(self, user: User, msg: IncomingMessage):
        self.user = user
        self.msg = msg
        self.wpp = WhatsAppService()

    def dispatch(self):

        if self.user.status is None:
            return idle_user_flow(ctx=self._build_prest_ctx())

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
            return idle_user_flow(ctx=self._build_prest_ctx())
        return dispacher()
    
    def _collecting_flow(self):
        return collecting_flow(ctx=self._build_prest_ctx())
    
    def _confirming(self):
        return confirming_flow(ctx=self._build_prest_ctx())
    
    def _address(self):
        return address_flow(ctx=self._build_prest_ctx())
    
    def _project(self):
        return project_flow(ctx=self._build_prest_ctx())
    
    def _certificate(self):
        return cerfiticate_flow(ctx=self._build_prest_ctx())
    
    def _active(self):
        return active_flow(ctx=self._build_tom_ctx())

    def _build_prest_ctx(self) -> ContextPrestador:
        return ContextPrestador(
            user=self.user,
            text=self.msg.text,
            new_data=PrestadorData(),
            db_data=PrestadorData(),
            merged=PrestadorData(),
            validated=PrestadorData(),
            msg_type=self.msg.tipo,
            button_id=self.msg.button_id
        )
    
    def _build_tom_ctx(self) -> ContextTomador:
        return ContextTomador(
            user=self.user,
            text=self.msg.text,
            new_data=TomadorData(),
            db_data=TomadorData(),
            merged=TomadorData(),
            validated=TomadorData(),
            msg_type=self.msg.tipo,
            button_id=self.msg.button_id
        )