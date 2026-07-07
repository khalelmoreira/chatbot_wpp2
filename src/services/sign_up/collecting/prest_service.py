from src.types import ContextPrestador, Role, ConvPrestStatus
from src.managers.conversations.register_conv_manager import RegisterConvManager
from src.managers.msg_manager import MsgManager

class ConvPrestService:
    def __init__(self, ctx: ContextPrestador):
        self.ctx = ctx
        self.conversation = RegisterConvManager(ctx)

    def tem_conv(self):
        conv = self._get_conv()
        if not conv:
            self._save_msg()
            return conv
        
        self._conv_id(conv)
        self._save_msg()
        return conv

    def _conv_id(self, conv):
        self.ctx.conversation_id = conv["id"]
        print(f"CTX.CONVERSATION_ID: {self.ctx.conversation_id}\n")

    def _save_msg(self):
        MsgManager(self.ctx).save_msg(role=Role.USER, content=self.ctx.text)

    def _get_conv(self):
        conv = self.conversation.get_ativa()
        print(f"CONVERSA: {conv}\n") if conv is None else print(f"CONVERSA: {dict(conv)}\n")
        return conv
    
class DispatchPrestService:
    def __init__(self, ctx: ContextPrestador):
        self.ctx = ctx
        self.conversation = RegisterConvManager(ctx)

    def dispatch(self, conv):

        if not conv:
            return idle_prest_flow(self.ctx, self.conversation)
        
        self.ctx.conv_status = self._status(conv)
        
        dispatchers = {
            ConvPrestStatus.COLLECTING: self._collecting_flow,
            ConvPrestStatus.CONFIRMING: self._confirming_flow,
        }

        dispatcher = dispatchers.get(self.ctx.conv_status)
        print(dispatcher)
        if dispatcher is None:
            return idle_prest_flow(self.ctx, self.conversation)
        return dispatcher()
    
    def _collecting_flow(self):
        return collecting_prest_flow()
    
    def _confirming_flow(self):
        return confirming_address()

    def _status(self, conv):
        status = conv["status"]
        print(f"STATUS: {status}\n")
        return status