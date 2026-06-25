from src.types import ContextTomador, IncomingMessage, ConversationStatus
from src.managers.conversations import ConversationManager
from src.managers.
from src.flows.active_flows import collecting_flow, confirming_flow, queued_flow
from src.utils.debug import print_table

class DispatchService:
    def __init__(self, ctx: ContextTomador, msg: IncomingMessage):
        self.ctx = ctx
        self.msg = msg
        self.conversation = ConversationManager(ctx)
        
    def dispatch(self):
        print(f"\n\n----------------TESTE FLUXO ATIVO_DISPATCHER----------------\n\n")

        conversa = self._get_conv
        if not conversa:
            self._save_msg()
            return self._collecting_flow()

        else:
            self._conv_id(conversa)
            self._save_msg()

        self.ctx.conv_status = self._status(conversa)

        dispatchers = {
            ConversationStatus.COLLECTING: self._collecting_flow,
            ConversationStatus.CONFIRMING: self._confirming_flow,
            ConversationStatus.QUEUED:     self._queued_flow,
        }

        dispatcher = dispatchers.get(self.ctx.conv_status)
        if dispatcher is None:
            raise ValueError(f"Estado não mapeado no fluxo: {self.ctx.conv_status}")
        return dispatcher()
    
    def _save_msg(self):

    
    def _collecting_flow(self):
        return collecting_flow(self.ctx, self.conversation)
    
    def _confirming_flow(self):
        return confirming_flow(self.ctx, self.conversation, self.msg)
    
    def _queued_flow(self):
        return queued_flow(self.ctx, self.conversation)

    def _get_conv(self):
        conversa = self.conversation.get_ativa()
        print(f"CONVERSA: {conversa}\n") if conversa is None else print(f"CONVERSA: {dict(conversa)}\n")
        return conversa
    
    def _conv_id(self, conversa):
        self.ctx.conversation_id = conversa["id"]
        print(f"CTX.CONVERSATION_ID: {self.ctx.conversation_id}\n")

    def _status(self, conversa):
        status = conversa["status"] if conversa else None
        print(f"STATUS: {status}\n")
        return status