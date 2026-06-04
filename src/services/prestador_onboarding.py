import httpx
from dataclasses import dataclass
from datetime import datetime

NOTAAS_BASE_URL = "https://platform.notaas.com.br/api/v1"

@dataclass
class Prestador:
    name: str
    cnpj: str
    razaoSocial: str
    incricaoMunicipal: str
    regimeTributario: str
    codigoMunicipio: str
    inscricaoEstadual: str

    endereco: Endereco

    email: str
    phone: str | None

    notaas_project_id: str | None
    notaas_api_key: str | None
    certificado_enviado: bool

    onboarding_status: str
    created_at: datetime

@dataclass
class Endereco:
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str
    cep: str


@dataclass
class ResultadoOnboarding:
    sucesso: bool
    project_id: str | None = None
    api_key: str | None = None
    erro: str | None = None

def criar_project(prestador: Prestador, org_token: str) -> ResultadoOnboarding:

    payload = {
        "name": prestador.razaoSocial,
        "cnpj": prestador.cnpj,
        "razaoSocial": prestador.razaoSocial,
        "incricaoMunicipal": prestador.incricaoMunicipal,
        "regimeTributario": prestador.regimeTributario,
        "codigoMunicipio": "3304557",
        "email": prestador.email,
        "endereco": {
            "logradouro": prestador.endereco.logradouro,
            "numero": prestador.endereco.numero,
            "complemento": prestador.endereco.complemento,
            "bairro": prestador.endereco.bairro,
            "cidade": prestador.endereco.cidade,
            "uf": prestador.endereco.uf,
            "cep": prestador.endereco.cep,
        }
    }

    with httpx.Client() as client:
        response = client.post(
            f"{NOTAAS_BASE_URL}/org/projects",
            json=payload,
            headers={"x-api-key": org_token}
        )

    if response.status_code == 409:
        # CNPJ já existe — recupera o project_id existente
        data = response.json()

        return ResultadoOnboarding(
            sucesso=True,
            project_id=data["existingProjectId"]
        )
    
    if response.status_code != 201:
        return ResultadoOnboarding(sucesso=False, erro=response.text)
    
    data = response.json()
    return ResultadoOnboarding(sucesso=True, project_id=data["id"])

def enviar_certificado(
        project_id: str,
        caminho_pfx: str,
        senha: str,
        org_token: str
) -> ResultadoOnboarding:

    with open(caminho_pfx, "rb") as f:

        with httpx.Client() as client:

            response = client.post(
                f"{NOTAAS_BASE_URL}/org/projects/{project_id}/certificate",
                files={"file": ("certificado.pfx", f, "applications/x-pkcs12")},
                data={"password": senha},
                headers={"x-api-key": org_token}
            )

        if response.status_code != 201:
            return ResultadoOnboarding(sucesso=False, erro=response.text)
        
        return ResultadoOnboarding(sucesso=True, project_id=project_id)
    
def criar_api_key(project_id: str, org_token: str) -> ResultadoOnboarding:

    with httpx.Client() as client:

        response = client.post(
            f"{NOTAAS_BASE_URL}/org/projects/{project_id}/api-keys",
            json={"name": "Backend producao"},
            headers={"x-api-key": org_token}
        )

    if response.status_code != 201:
        return ResultadoOnboarding(sucesso=False, erro=response.text)
    
    data = response.json()

    return ResultadoOnboarding(
        sucesso=True,
        project_id=project_id,
        api_key=data["key"]
    )

def onboarding_completo(
        prestador: Prestador,
        caminho_pfx: str,
        senha_certificado: str,
        org_token: str
) -> ResultadoOnboarding:
    
    resultado = criar_project(prestador, org_token)
    if not resultado.sucesso:
        return resultado
    
    project_id = resultado.project_id

    resultado = enviar_certificado(project_id, caminho_pfx, senha_certificado, org_token)
    if not resultado.sucesso:
        return resultado
    
    resultado = criar_api_key(project_id, org_token)
    if not resultado.sucesso:
        return resultado
    
# def retomar_onboarding(prestador: Prestador, ...) -> ResultadoOnboarding:
#     # já tem project_id? pula o passo 1
#     if not prestador.notaas_project_id:
#         ...criar projeto...

#     # já enviou certificado? pula o passo 2
#     if not prestador.certificado_enviado:
#         ...enviar certificado...

#     # já tem api_key? pula o passo 3
#     if not prestador.notaas_api_key:
#         ...criar api key...