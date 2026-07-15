from src.types import ContextPrestador
from src.services.register.collecting.prest_service import ConvPrestService, DispatchPrestService as Dispatcher

def prest_flow(ctx: ContextPrestador):

    print(f"\n\n----------------PREST FLOW----------------\n\n")

    conv = ConvPrestService(ctx)
    dispatch = Dispatcher(ctx)