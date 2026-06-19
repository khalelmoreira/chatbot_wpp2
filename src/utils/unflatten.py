from dataclasses import asdict
from typing import Any
from src.types import DadosTomador, ResultadoValidacao, Tomador, Servico, Valores

def unflatten(flat: dict[str, Any]) -> dict[str, Any]:
    
    result: dict[str, Any] = {}
    for key, value in flat.items():
        secao, attr = key.split(".")
        result.setdefault(secao, {})[attr] = value
    return result