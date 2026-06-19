from typing import Any
from src.types import DadosTomador, Tomador, Servico, Valores

def unpack_dados_db(data: dict[str, Any]) -> DadosTomador:

    tomador_data = data.get("tomador") or {}
    servico_data = data.get("servico") or {}
    valores_data = data.get("valores") or {}

    return DadosTomador(
        tomador=Tomador(**tomador_data),
        servico=Servico(**servico_data),
        valores=Valores(**valores_data),
    )