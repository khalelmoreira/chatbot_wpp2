import re
from enum import StrEnum
from dataclasses import fields as dataclass_fields
from typing import Any
from src.types.context_prestador import ContextPrestador
from src.types.context_base import ResultadoValidacao

class RegimeTributario(StrEnum):
    NORMAL = "1"
    MEI = "2"
    SIMPLES = "3"
    SIMPLES_EXCESSO = "3e"

def extrair_digitos(valor: str | None) -> str | None:
    if not valor:
        return None
    resultado = re.sub(r'\D', '', valor)
    return resultado if resultado else None

def validar_razao_social(razao_social: str | None) -> bool:

    if not razao_social:
        return False
    
    razao_social = razao_social.strip()

    if len(razao_social) < 3:
        return False
    
    return True

def validar_cnpj(cnpj: str | None) -> bool:

    cnpj = extrair_digitos(cnpj)

    if not cnpj:
        return False
    
    if len(cnpj) != 14:
        return False
    
    if not cnpj.isdigit():
        return False
    
    if cnpj == cnpj[0] * 14:
        return False
    
    def calcular_digit(numbers: str, weights: list[int]) -> str:
        soma = sum(
            int(n) * p
            for n, p in zip(numbers, weights)
        )

        resto = soma % 11

        return "0" if resto < 2 else str(11 - resto)
    
    weights1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    weights2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]

    dv1 = calcular_digit(cnpj[:12], weights1)
    dv2 = calcular_digit(cnpj[:12] + dv1, weights2)

    return cnpj[-2:] == dv1 + dv2

def validar_email(email: str | None) -> bool:

    if not email:
        return False
    
    if "@" not in email:
        return False
    
    try:
        user, dominio = email.split("@")
    except ValueError:
        return False
    
    if not user:
        return False
    
    if "." not in dominio:
        return False
    
    return True

def validar_reg_trib(regime: str | None) -> bool:
    return regime in RegimeTributario._value2member_map_

def validar_cep(cep: str | None) -> bool:

    cep = extrair_digitos(cep)

    if not cep:
        return False
    
    if len(cep) != 8:
        return False
    
    return cep.isdigit()

def validar_inscricao_municipal(im: str | None) -> bool:

    if not im:
        return False
    
    if len(im) < 3:
        return False
    
    return im.isalnum()

_VALIDACOES_PRESTADOR: dict[str, callable[[Any], bool]] = {
    "cnpj": validar_cnpj,
    "razao_social": validar_razao_social,
    "email": validar_email,
    "regime_tributario": validar_reg_trib,
    "cep": validar_cep,
    "inscricao_municipal": validar_inscricao_municipal,
}

class ValidadorPrestador:

    def validar(self, ctx: ContextPrestador) -> None:

        dados = ctx.dados_completos

        validos: dict[str, Any] = {}
        invalidos: list[str] = []
        faltantes: list[str] = []

        for campo, fn_validar in _VALIDACOES_PRESTADOR.items():
            valor = getattr(dados, campo, None)

            if valor is None:
                faltantes.append(campo)
            
            elif not fn_validar(valor):
                invalidos.append(campo)

            else:
                validos[campo] = valor

        ctx.validacao = ResultadoValidacao(
            validos=validos,
            invalidos=invalidos,
            faltantes=faltantes,
        )