import re
from enum import StrEnum
from typing import Any, Callable
from src.types import ContextPrestador, ResultadoValidacao

class RegimeTributario(StrEnum):
    NORMAL = "1"
    MEI = "2"
    SIMPLES = "3"
    SIMPLES_EXCESSO = "3e"

def val_generic_str(campo: str) -> bool:    
    campo = campo.strip()

    if len(campo) < 3:
        return False
    
    return True

def extrair_digitos(valor: str | None) -> str | None:
    if not valor:
        return None
    resultado = re.sub(r'\D', '', valor)
    return resultado if resultado else None

def val_r_social(razao_social: str | None) -> bool:

    if not razao_social:
        return False
    
    razao_social = razao_social.strip()

    if len(razao_social) < 3:
        return False
    
    return True

def val_cnpj(cnpj: str | None) -> bool:

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

def val_email(email: str | None) -> bool:

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

def val_reg_trib(regime: str | None) -> bool:
    return regime in RegimeTributario._value2member_map_

def val_cep(cep: str | None) -> bool:

    cep = extrair_digitos(cep)

    if not cep:
        return False
    
    if len(cep) != 8:
        return False
    
    return cep.isdigit()

def val_logr(logradouro: str | None) -> bool:
    if not logradouro:
        return False
    
    valido = val_generic_str(logradouro)
    if not valido:
        return False
    return True

def val_bairro(bairro: str | None) -> bool:
    if not bairro:
        return False
    
    valido = val_generic_str(bairro)
    if not valido:
        return False
    return True

def val_cidade(cidade: str | None) -> bool:
    if not cidade:
        return False
    
    valido = val_generic_str(cidade)
    if not valido:
        return False
    return True

def val_uf(uf: str | None) -> bool:
    if not uf:
        return False
    
    uf = uf.strip()

    if len(uf) < 2:
        return False
    
    return True

_VALIDATIONS_PRESTADOR: dict[str, Callable[[Any], bool]] = {
    "cnpj":              val_cnpj,
    "razao_social":      val_r_social,
    "email":             val_email,
    "regime_tributario": val_reg_trib,
    "cep":               val_cep,
}

_VALIDATIONS_ADDRESS: dict[str, Callable[[Any], bool]] = {
    "logradouro":  val_logr,
    "bairro":      val_bairro,
    "cidade":      val_cidade,
    "uf":          val_uf,
}

class ValidadorPrestador:

    def validar(self, ctx: ContextPrestador) -> None:

        validos: dict[str, Any] = {}
        invalidos: list[str] = []
        faltantes: list[str] = []
        
        dados = ctx.dados_completos

        for campo, fn_validar in _VALIDATIONS_PRESTADOR.items():
            valor = getattr(dados, campo, None)
            self._checar(campo, valor, fn_validar, validos, invalidos, faltantes)

        endereco = dados.endereco
        for campo, fn_validar in _VALIDATIONS_ADDRESS.items():
            valor = getattr(endereco, campo, None) if endereco is not None else None
            self._checar(campo, valor, fn_validar, validos, invalidos, faltantes)

        ctx.validacao = ResultadoValidacao(
            validos=validos,
            invalidos=invalidos,
            faltantes=faltantes,
        )

    @staticmethod
    def _checar(campo, valor, fn_validar, validos, invalidos, faltantes):
        if valor is None:
            faltantes.append(campo)
        elif not fn_validar(valor):
            invalidos.append(campo)
        else:
            validos[campo] = valor