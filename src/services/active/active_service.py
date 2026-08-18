from src.flows.active_flows.collecting_flow import collecting_flow
from src.flows.active_flows.confirming_flow import confirming_flow
from src.flows.active_flows.idle_flow import idle_flow
from src.flows.active_flows.queued_flow import queued_flow
from src.managers.conversations import ConvManager
from src.managers.msg_manager import MsgManager
from src.types import ContextTomador, ConvStatus, Role
from src.types.conversation import Conversation
from src.utils.debug import print_table


class ConvActiveService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.conversation = ConvManager(ctx)
    
    def tem_conv(self):
        conversa = self._get_conv()
        if conversa is None:
            self._save_msg()
            return conversa

        self.ctx.conv_id = conversa.id
        self._save_msg()
        return conversa
    
    def _save_msg(self):
        msg = MsgManager(self.ctx)
        msg.save_msg(role=Role.USER, content=self.ctx.text)
        print_table(table_name="messages", where="phone = ?", params=(self.ctx.user.phone,))

    def _get_conv(self):
        conversa = self.conversation.get_ativa()
        print(f"CONVERSA: {conversa}\n")
        return conversa

class DispatchActiveService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.conversation = ConvManager(ctx)
        
    def dispatch(self, conversa: Conversation):
        print("\n\n----------------TESTE FLUXO ATIVO_DISPATCHER----------------\n\n")

        if not conversa:
            return idle_flow(self.ctx, self.conversation)
        
        self.ctx.conv_status = conversa.status

        dispatchers = {
            ConvStatus.COLLECTING: self._collecting_flow,
            ConvStatus.CONFIRMING: self._confirming_flow,
            ConvStatus.QUEUED:     self._queued_flow,
        }

        dispatcher = dispatchers.get(self.ctx.conv_status)
        print(dispatcher)
        if dispatcher is None:
            return idle_flow(self.ctx, self.conversation)
        return dispatcher()
    
    def _collecting_flow(self):
        return collecting_flow(self.ctx, self.conversation)
    
    def _confirming_flow(self):
        return confirming_flow(self.ctx, self.conversation)
    
    def _queued_flow(self):
        return queued_flow(self.ctx, self.conversation)