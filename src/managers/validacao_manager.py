from dataclasses import fields as dataclass_fields
from typing import Any
from src.utils.validacao import validar_cnpj, validar_cep, validar_email, validar_inscricao_municipal, validar_razao_social, validar_reg_trib
from src.types.context_prestador import ContextPrestador
from src.types.context_base import ResultadoValidacao

_VALIDACOES_PRESTADOR: dict[str, callable[[Any], bool]] = {
    "cnpj": validar_cnpj,
    "razao_social": validar_razao_social,
    "email": validar_email,
    "regime_tributario": validar_reg_trib,
    "cep": validar_cep,
    "inscricao_municipal": validar_inscricao_municipal,
}

class ValidadorPrestadorManager:

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