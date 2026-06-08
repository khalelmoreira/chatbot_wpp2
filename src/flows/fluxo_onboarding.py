import httpx
import os
from src.types.context_prestador import Endereco, ProjectPrestador
from src.types.context_prestador import ResultadoOnboarding
from src.managers.prestador_manager import PrestadorManager

NOTAAS_BASE_URL = "https://platform.notaas.com.br/api/v1"

ORG_TOKEN = os.getenv("NOTAAS_ORG_TOKEN")

def criar_project_apikey(phone: str) -> ResultadoOnboarding:

    """
    Executa as etapas síncronas do onboarding: projeto + api key.
    Idempotente: retoma de onde parou se chamada novamente.
    """

    prestador_manager = PrestadorManager()
    prestador = prestador_manager.get_all(phone)

    if prestador is None:
        return ResultadoOnboarding(sucesso=False, erro="Prestador nao encontrado.")
    
    project_id = prestador.notaas_project_id

    # Passo 1: criar projeto (pula se já existe)
    if not project_id:
        resultado = criar_project(phone)

        if not resultado.sucesso:
            return resultado
        
        project_id = resultado.project_id
        prestador_manager.salvar_project_id(phone, project_id)

    # Passo 2: criar api key (pula se já existe)
    if not prestador.notaas_api_key:
        resultado = criar_api_key(project_id)
        if not resultado.sucesso:
            return resultado
        
        prestador_manager.salvar_apikey(phone, resultado.api_key)

    return ResultadoOnboarding(sucesso=True, project_id=project_id)

def criar_project(phone: str) -> ResultadoOnboarding:

    prestador_manager = PrestadorManager()
    prestador = prestador_manager.get_all(phone)

    payload = {
        "name": prestador.razaoSocial,
        "cnpj": prestador.cnpj,
        "razaoSocial": prestador.razaoSocial,
        "inscricaoMunicipal": prestador.inscricaoMunicipal,
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
        senha: str
) -> ResultadoOnboarding:

    with open(caminho_pfx, "rb") as f:

        with httpx.Client() as client:

            response = client.post(
                f"{NOTAAS_BASE_URL}/org/projects/{project_id}/certificate",
                files={"file": ("certificado.pfx", f, "application/x-pkcs12")},
                data={"password": senha},
                headers={"x-api-key": org_token}
            )

        if response.status_code != 201:
            return ResultadoOnboarding(sucesso=False, erro=response.text)
        
        return ResultadoOnboarding(sucesso=True, project_id=project_id)
    
def criar_api_key(project_id: str) -> ResultadoOnboarding:

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
        senha_certificado: str
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
    
def retomar_onboarding(prestador: Prestador, ...) -> ResultadoOnboarding:
    # já tem project_id? pula o passo 1
    if not prestador.notaas_project_id:
        ...criar projeto...

    # já enviou certificado? pula o passo 2
    if not prestador.certificado_enviado:
        ...enviar certificado...

    # já tem api_key? pula o passo 3
    if not prestador.notaas_api_key:
        ...criar api key...