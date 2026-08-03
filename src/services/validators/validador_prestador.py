from dataclasses import dataclass
from operator import truediv
import re
from enum import StrEnum
from typing import Any, Callable, Generic, TypeVar
from src.types.user import PrestadorData
from src.types import ContextPrestador, ValidationResult, Address, Mergeable

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

T = TypeVar('T', bound=Mergeable)

@dataclass
class ValidationOutput(Generic[T]):
    valid:  T
    result: ValidationResult


def _validar(
    data: T,
    validations: dict[str, Callable],
    factory: Callable[[], T],
    prefix: str = "",
) -> ValidationOutput[T]:

    valid = factory()
    invalid: list[str] = []
    missing: list[str] = []
    
    for campo, fn_validar in validations.items():
        valor = getattr(data, campo, None)
        _checar(campo, valor, fn_validar, valid, invalid, missing, prefix)

    return ValidationOutput(
        valid=valid,
        result=ValidationResult(invalid=invalid, missing=missing),
    )   


def _checar(campo, valor, fn_validar, target, invalid, missing, prefix="") -> bool:
    key = f"{prefix}{campo}"

    if valor is None:
        missing.append(key)
        return False
    
    elif not fn_validar(valor):
        invalid.append(key)
        return False
    
    else:
        setattr(target, campo, valor)
        return True

class ValidatorPrestador:
    @staticmethod
    def validar(data: PrestadorData) -> ValidationOutput[PrestadorData]:
        output = _validar(data, _VALIDATIONS_PRESTADOR, PrestadorData)

        if data.address is not None:
            address_output = ValidatorAddress.validar(data.address)

            output.valid.address = address_output.valid
            output.result.invalid.extend(f"address.{c}"for c in address_output.result.invalid)
            output.result.missing.extend(f"address.{c}"for c in address_output.result.missing)

        return output

class ValidatorAddress:
    @staticmethod
    def validar(data: Address) -> ValidationOutput[Address]:
        return _validar(data, _VALIDATIONS_ADDRESS, Address)