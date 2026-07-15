from src.types import ContextTomador
from src.services.active.active_service import DispatchActiveService, ConvActiveService

def active_flow(ctx: ContextTomador):

    print(f"\n\n----------------ACTIVE FLOW----------------\n\n")

    conv = ConvActiveService(ctx)
    dispatch = DispatchActiveService(ctx)

    conversa = conv.tem_conv()
    dispatch.dispatch(conversa)