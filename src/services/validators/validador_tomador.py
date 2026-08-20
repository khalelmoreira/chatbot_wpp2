from operator import attrgetter
from typing import Any, Callable

from src.services.validators.validador_prestador import val_cnpj
from src.types import ContextTomador, TomadorData, ValidationResult


def validar_nome(nome: str | None) -> bool:

    if not nome:
        return False
    return len(nome.strip()) >= 2

def validar_descricao(descricao: str | None) -> bool:

    if not descricao:
        return False
    return len(descricao.strip()) >= 3

def validar_valor_total(total: Any) -> bool:

    if total is None:
        return False
    
    try:
        return float(total) > 0
    
    except (ValueError, TypeError):
        return False
    
_VALIDACOES_TOMADOR: dict[str, Callable[[Any], bool]] = {
    "tomador.nome":        validar_nome,
    "tomador.cnpj":        val_cnpj,
    "servico.descricao":   validar_descricao,
    "valores.total":       validar_valor_total,
}

class ValidadorTomador:

    def validar(self, ctx: ContextTomador) -> None:

        dados = ctx.merged

        valid = TomadorData()
        invalidos: list[str] = []
        faltantes: list[str] = []

        for campo, fn_validar in _VALIDACOES_TOMADOR.items():

            secao, attr = campo.split(".")
            valor = attrgetter(campo)(dados)

            if valor is None:
                faltantes.append(campo)

            elif not fn_validar(valor):
                invalidos.append(campo)

            else:
                setattr(getattr(valid, secao), attr, valor)

        ctx.valid = valid
        ctx.validation = ValidationResult(
            invalid=invalidos,
            missing=faltantes,
        )