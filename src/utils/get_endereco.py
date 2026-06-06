import requests
from src.types.context_prestador import Endereco

def get_endereco_by_cep(cep: str) -> Endereco | None:

    url = f"https://viacep.com.br/ws/{cep}/json/"

    response = requests.get(url)

    if response.status_code != 200:
        return None
    
    data = response.json()

    if data.get("erro"):
        return None
    
    return Endereco(
        logradouro=data["logradouro"],
        numero=data["numero"],
        bairro=data["bairro"],
        cidade=data["localidade"],
        uf=data["uf"],
    )