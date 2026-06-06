import re
from enum import StrEnum
from src.types.context_nfse import ContextNfse, DadosNfse
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