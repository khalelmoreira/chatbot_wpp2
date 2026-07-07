from typing import Any
from src.types import DadosTomador

def unpack_dados_db(data: dict[str, Any]) -> DadosTomador:
    return DadosTomador.from_dict(data)