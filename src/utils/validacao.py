import re
from copy import deepcopy
import hmac
import hashlib
import os
from src.types.context_cadastro import ContextCadastro
from src.types.context_nfse import ContextNfse, DadosNfse
from src.types.context_base import ResultadoValidacao

def cpf_valido(cpf: str) -> bool

def validar_dados_mensagem(ctx: ContextCadastro) -> None:
    
    dados = ctx.dados_completos

    validos: dict[str, str] = {}
    invalidos: list[str] = []
    faltantes: list[str] = []

    nome = dados.nome

    if not nome or len(nome.strip()) < 3:
        faltantes.append("nome")

    else:
        validos["nome"] = nome.strip()

    cpf_cnpj_raw = dados.cpf_cnpj

    if cpf_cnpj_raw is None:
        faltantes.append("cpf_cnpj")

    else:
        limpo = re.sub(r"\D", "", cpf_cnpj_raw)

        if len(limpo) == 11 and cpf_valido(limpo):
            validos["cpf_cnpj"] = limpo
            validos["tipo_pessoa"] = "F"

        elif len(limpo) == 14 and cnpj_valido(limpo)

        cpf_cnpj_limpo = re.sub(r"\D", "", cpf_cnpj_raw)

        if len(cpf_cnpj_limpo) in [11, 14]:
            validos["cpf_cnpj_raw"] = cpf_cnpj_limpo

        else:
            invalidos.append("cpf_cnpj_raw")

    email = dados.email

    if email is None:
        faltantes.append("email")

    elif re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        validos["email"] = email.strip().lower()

    else:
        invalidos.append("email")


    ctx.validacao = ResultadoValidacao(
        validos=validos,
        invalidos=invalidos,
        faltantes=faltantes
    )

def normalizar_dados_nf(ctx: ContextNfse) -> DadosNfse:

    dados = ctx.dados_completos

    print(f"MERGEOU: {dados}\n")

    resultado = DadosNfse()

    if dados.tomador.nome:
        resultado.tomador.nome = dados.tomador.nome.strip()

    if dados.tomador.cnpj:
        resultado.tomador.cnpj = re.sub(
            r"\D",
            "",
            str(dados.tomador.cnpj)
        )

    if dados.valores.total is not None:
        try:
            resultado.valores.total = float(
                dados.valores.total
            )
        
        except:
            resultado.valores.total = None

    if dados.valores.aliquotaIss is not None:
        try:
            resultado.valores.aliquotaIss = float(
                dados.valores.aliquotaIss
            )
        
        except:
            resultado.valores.aliquotaIss = None

    ctx.dados_normalizados = resultado

def validar_dados_nf(ctx: ContextNfse) -> None:

    dados = ctx.dados_normalizados

    print(f"VALIDADOR RECEBE: {dados}\n")

    validos = {}
    invalidos = []
    faltantes = []

    nome = dados.tomador.nome
    cnpj = dados.tomador.cnpj

    if not nome or not str(nome).strip():
        faltantes.append("nome")

    else:
        validos["tomador.nome"] = nome

    
    if not cnpj or not str(cnpj).strip():
        faltantes.append("tomador.cnpj")

    else:
        validos["tomador.cnpj"] = cnpj

    descricao = dados.servico.descricao

    if not descricao or not str(descricao).strip():
        faltantes.append("servico.descricao")

    else:
        validos["servico.descricao"] = descricao

    total = dados.valores.total

    if total is None:
        faltantes.append("valores.total")

    elif not isinstance(total, (int, float)):
        invalidos.append("valores.total")

    elif total <= 0:
        invalidos.append("valores.total")

    else:
        validos["valores.total"] = str(total)

    aliquota = dados.valores.aliquotaIss

    if aliquota is None:
        faltantes.append("valores.aliquotaIss")

    elif not isinstance(aliquota, (int, float)):
        invalidos.append("valores.aliquotaIss")

    elif aliquota < 0:
        invalidos.append("valores.aliquotaIss")

    else:
        validos["valores.aliquotaIss"] = str(aliquota)
    
    ctx.validacao = ResultadoValidacao(
        validos=validos,
        invalidos=invalidos,
        faltantes=faltantes
    )

#def validar_assinatura(request):

#     assinatura_recebida = request.headers.get("X-Hub-Signature-256")

#     if not assinatura_recebida:
#         return False
    
#     assinatura_recebida = assinatura_recebida.split("=")[1]

#     body = request.get_data()

#     hash_gerado = hmac.new(
#         os.getenv("APP_SECRET").encode("utf-8"),
#         body,
#         hashlib.sha256
#     ).hexdigest()

#     return hmac.compare_digest(hash_gerado, assinatura_recebida)