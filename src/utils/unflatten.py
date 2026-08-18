from typing import Any


def unflatten(flat: dict[str, Any]) -> dict[str, Any]:
    
    result: dict[str, Any] = {}
    for key, value in flat.items():
        secao, attr = key.split(".")
        result.setdefault(secao, {})[attr] = value
    return result