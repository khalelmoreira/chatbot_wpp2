from src.types import ContextTomador, IncomingMessage
from src.services.active.dispatch_service import DispatchService

def active_flow(ctx: ContextTomador, msg: IncomingMessage):

    print(f"\n\n----------------ACTIVE FLOW----------------\n\n")

    dispatch = DispatchService(ctx, msg)
    dispatch.dispatch()