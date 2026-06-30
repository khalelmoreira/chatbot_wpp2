from src.types import ContextTomador, IncomingMessage
from src.services.active.active_service import DispatchActiveService, ConvActiveService

def active_flow(ctx: ContextTomador, msg: IncomingMessage):

    print(f"\n\n----------------ACTIVE FLOW----------------\n\n")

    conv = ConvActiveService(ctx)
    dispatch = DispatchActiveService(ctx, msg)

    conversa = conv.tem_conv()
    dispatch.dispatch(conversa)