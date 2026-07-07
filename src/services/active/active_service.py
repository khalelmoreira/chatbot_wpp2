from src.types import ContextTomador, IncomingMessage, ConversationStatus, Role
from src.managers.conversations import ConversationManager
from chatbot_wpp2.src.managers.msg_manager import MsgManager
from src.flows.active_flows.collecting_flow import collecting_flow
from src.flows.active_flows.confirming_flow import confirming_flow
from src.flows.active_flows.queued_flow import queued_flow
from src.flows.active_flows.idle_flow import idle_flow
from src.utils.debug import print_table

class ConvActiveService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.conversation = ConversationManager(ctx)
    
    def tem_conv(self):
        conversa = self._get_conv()
        if not conversa:
            self._save_msg()
            return conversa

        self._conv_id(conversa)
        self._save_msg()
        return conversa
    
    def _save_msg(self):
        msg = MsgManager(self.ctx)
        msg.save_msg(role=Role.USER, content=self.ctx.text)
        print_table(table_name="messages", where="phone = ?", params=(self.ctx.user.phone,))

    def _conv_id(self, conversa):
        self.ctx.conversation_id = conversa["id"]
        print(f"CTX.CONVERSATION_ID: {self.ctx.conversation_id}\n")

    def _get_conv(self):
        conversa = self.conversation.get_ativa()
        print(f"CONVERSA: {conversa}\n") if conversa is None else print(f"CONVERSA: {dict(conversa)}\n")
        return conversa

class DispatchActiveService:
    def __init__(self, ctx: ContextTomador, msg: IncomingMessage):
        self.ctx = ctx
        self.msg = msg
        self.conversation = ConversationManager(ctx)
        
    def dispatch(self, conversa):
        print(f"\n\n----------------TESTE FLUXO ATIVO_DISPATCHER----------------\n\n")

        if not conversa:
            return idle_flow(self.ctx, self.conversation)
        
        self.ctx.conv_status = self._status(conversa)

        dispatchers = {
            ConversationStatus.COLLECTING: self._collecting_flow,
            ConversationStatus.CONFIRMING: self._confirming_flow,
            ConversationStatus.QUEUED:     self._queued_flow,
        }

        dispatcher = dispatchers.get(self.ctx.conv_status)
        print(dispatcher)
        if dispatcher is None:
            return idle_flow(self.ctx, self.conversation)
        return dispatcher()
    
    
    def _collecting_flow(self):
        return collecting_flow(self.ctx, self.conversation)
    
    def _confirming_flow(self):
        return confirming_flow(self.ctx, self.conversation, self.msg)
    
    def _queued_flow(self):
        return queued_flow(self.ctx, self.conversation)

    def _status(self, conversa):
        status = conversa["status"]
        print(f"STATUS: {status}\n")
        return status