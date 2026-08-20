import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.collecting_user_service import (
    AddressService,
    CnpjService,
    ExtractionService,
    ValidationService,
)
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def collecting_flow(ctx: ContextPrestador) -> None:

    logger.debug("collecting_user_flow: user_id=%s", ctx.user.id)

    prestador = PrestadorManager(ctx)
    validation = ValidationService(ctx, prestador)

    ExtractionService(ctx, prestador).extract_e_merge()

    if not validation.valido():
        return

    if not validation.completo():
        return

    if not CnpjService(ctx, prestador).verificar():
        return

    AddressService(ctx, prestador).address()