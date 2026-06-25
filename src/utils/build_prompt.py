def build_prompt(template: str, params: list) -> str:
    return template.format(*params)