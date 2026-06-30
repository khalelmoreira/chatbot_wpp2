from typing import Any

def build_list_prompt(template: str, params: list[Any] | tuple | dict[Any, Any]) -> str:
    if isinstance(params, dict):
        return template.format(**params)
    return template.format(*params)