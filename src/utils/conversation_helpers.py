import json
from src.models.conversation_constantes import CAMPOS_OBRIGATORIOS, CANCEl_WORDS, CONFIRM_WORDS

def campos_faltando(dados: dict) -> list[tuple]:

    faltando = []

    for secao, campo in CAMPOS_OBRIGATORIOS:
        valor = dados.get(secao, {}).get(campo)
        if not valor:
            faltando.append((secao, campo))

    return faltando

def merge_draft(atual: dict, extraido: dict) -> dict:

    """Merge profundo — não substitui o draft inteiro, só atualiza campos presentes."""

    resultado = json.loads(json.dumps(atual))    # deep copy sem dependência externa

    for secao, campos in extraido.items():
        if isinstance(campos, dict):
            if secao not in resultado:
                resultado[secao] = {}
            
            for campo, valor in campos.items():
                if valor is not None:                     # nunca sobrescreve com None
                    resultado[secao][campo] = valor

    return resultado

def is_cancel(message: str) -> bool:
    return message.strip().lower() in CANCEl_WORDS

def is_confirm(message: str) -> bool:
    return message.strip().lower() in CONFIRM_WORDS