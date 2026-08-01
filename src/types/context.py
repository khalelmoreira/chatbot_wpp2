from dataclasses import dataclass
from src.types.base import ContextBase
from src.types.user import PrestadorData
from src.types.tomador import TomadorData

@dataclass
class ContextPrestador(ContextBase[PrestadorData]):
    conv_id: int | None = None
    idempotency_key: str = ""

@dataclass
class ContextTomador(ContextBase[TomadorData]):
    conv_id:         int | None = None
    idempotency_key: str = ""
    conv_status:     str | None = None