from src.flows.active_flows import active_flow
from src.flows.user_flows.address_flow import address_flow
from src.flows.user_flows.certificate_flow import cerfiticate_flow
from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.flows.user_flows.confirming_user_flow import confirming_flow
from src.flows.user_flows.idle_user_flow import idle_user_flow
from src.flows.user_flows.project_flow import project_flow
from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager, UserManager
from src.services.active.exit_command import SIGNUP_EXIT_CONFIRMATION_MSG, is_exit_command
from src.services.sender import get_sender
from src.types import (
    Address,
    ContextPrestador,
    ContextTomador,
    IncomingMessage,
    MsgType,
    PrestadorData,
    Role,
    TomadorData,
    User,
    UserStatus,
)
from src.utils.build_ctx import build_ctx

# Etapas do onboarding em que a palavra de saída ("cancelar") abandona o cadastro
# e devolve o usuário ao ponto de partida — espelha COLLECTING/CONFIRMING no
# fluxo de emissão. ACTIVE e os estados terminais ficam de fora.
_ETAPAS_CANCELAVEIS = frozenset({
    UserStatus.COLLECTING,
    UserStatus.ADDRESS,
    UserStatus.CONFIRMING,
    UserStatus.PROJECT,
    UserStatus.CERTIFICATE,
})


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
                name=self.msg.name,
                channel=self.msg.channel,
            )
            return user, True

        return user, False

class DispatchUser:
    def __init__(self, user: User, msg: IncomingMessage):
        self.user = user
        self.msg = msg
        self.wpp = get_sender(self.user.channel)

    def dispatch(self):

        if self.user.status is None:
            return idle_user_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))

        if self._quer_sair():
            return self._cancelar_cadastro()

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
    
    def _quer_sair(self) -> bool:
        """Palavra de saída digitada durante o onboarding. Só texto — um clique de
        botão nunca é uma palavra de saída."""
        return (
            self.user.status in _ETAPAS_CANCELAVEIS
            and self.msg.tipo == MsgType.TEXT
            and is_exit_command(self.msg.text)
        )

    def _cancelar_cadastro(self):
        ctx = build_ctx(ContextPrestador, PrestadorData, self.user, self.msg)
        PrestadorManager(ctx).update_state(UserStatus.CANCELLED)
        MsgManager(self.user).save_msg(Role.AI, SIGNUP_EXIT_CONFIRMATION_MSG)
        self.wpp.send_msg_text(self.user.phone, SIGNUP_EXIT_CONFIRMATION_MSG)

    def _collecting_flow(self):
        return collecting_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _confirming(self):
        return confirming_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _address(self):
        return address_flow(ctx=build_ctx(ContextPrestador, Address, self.user, self.msg))
    
    def _project(self):
        return project_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _certificate(self):
        return cerfiticate_flow(ctx=build_ctx(ContextPrestador, PrestadorData, self.user, self.msg))
    
    def _active(self):
        return active_flow(ctx=build_ctx(ContextTomador, TomadorData, self.user, self.msg))