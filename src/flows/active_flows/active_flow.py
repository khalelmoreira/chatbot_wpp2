from src.services.active.active_service import ConvActiveService, DispatchActiveService
from src.types import ContextTomador


def active_flow(ctx: ContextTomador):

    print("\n\n----------------ACTIVE FLOW----------------\n\n")

    conv = ConvActiveService(ctx)
    dispatch = DispatchActiveService(ctx)

    conversa = conv.tem_conv()
    dispatch.dispatch(conversa)