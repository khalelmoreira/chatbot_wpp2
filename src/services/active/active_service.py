import logging

from src.flows.active_flows.collecting_flow import collecting_flow
from src.flows.active_flows.confirming_flow import confirming_flow
from src.flows.active_flows.idle_flow import idle_flow
from src.flows.active_flows.queued_flow import queued_flow
from src.managers.conversations import ConvManager
from src.managers.msg_manager import MsgManager
from src.services.active.exit_command import EXIT_CONFIRMATION_MSG, is_exit_command
from src.services.sender import get_sender
from src.types import ContextTomador, ConvStatus, MsgType, Role
from src.types.conversation import Conversation

logger = logging.getLogger(__name__)

class ConvActiveService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.conversation = ConvManager(ctx)
    
    def tem_conv(self):
        conversa = self._get_conv()
        if conversa is None:
            return conversa

        self.ctx.conv_id = conversa.id
        return conversa

    def _get_conv(self):
        conversa = self.conversation.get_ativa()
        if conversa is not None:
            logger.debug("conversa ativa: id=%s status=%s", conversa.id, conversa.status)
        return conversa

class DispatchActiveService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.conversation = ConvManager(ctx)

    def dispatch(self, conversa: Conversation):

        if not conversa:
            return idle_flow(self.ctx, self.conversation)

        self.ctx.conv_status = conversa.status

        if self._quer_sair():
            return self._cancelar_conversa()

        dispatchers = {
            ConvStatus.COLLECTING: self._collecting_flow,
            ConvStatus.CONFIRMING: self._confirming_flow,
            ConvStatus.QUEUED:     self._queued_flow,
        }

        dispatcher = dispatchers.get(self.ctx.conv_status)
        logger.debug("active_dispatcher: conv_id=%s status=%s", conversa.id, self.ctx.conv_status)
        if dispatcher is None:
            return idle_flow(self.ctx, self.conversation)
        return dispatcher()

    def _quer_sair(self) -> bool:
        """Palavra de saída digitada durante a coleta ou a confirmação. Só texto —
        um clique de botão nunca é uma palavra de saída."""
        return (
            self.ctx.conv_status in (ConvStatus.COLLECTING, ConvStatus.CONFIRMING)
            and self.ctx.msg_type == MsgType.TEXT
            and is_exit_command(self.ctx.text)
        )

    def _cancelar_conversa(self):
        self.conversation.update_state(ConvStatus.CANCELLED)
        MsgManager(self.ctx.user).save_msg(Role.AI, EXIT_CONFIRMATION_MSG)
        get_sender(self.ctx.user.channel).send_msg_text(self.ctx.user.phone, EXIT_CONFIRMATION_MSG)

    def _collecting_flow(self):
        return collecting_flow(self.ctx, self.conversation)
    
    def _confirming_flow(self):
        return confirming_flow(self.ctx, self.conversation)
    
    def _queued_flow(self):
        return queued_flow(self.ctx, self.conversation)