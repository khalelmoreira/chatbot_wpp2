from typing import Any
from src.types import TomadorData

def unpack_dados_db(data: dict[str, Any]) -> TomadorData:
    return TomadorData.from_dict(data)