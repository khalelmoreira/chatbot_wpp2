from src.types import ContextTomador, IncomingMessage
from src.services.active.dispatch_service import DispatchService
from src.flows.active_flows import collecting_flow

def active_flow(ctx: ContextTomador, msg: IncomingMessage):

    print(f"\n\n----------------ACTIVE FLOW----------------\n\n")

    dispatch = DispatchService(ctx, msg)
    conv = dispatch.criar_conv_se()
    dispatch.dispatch(conv)