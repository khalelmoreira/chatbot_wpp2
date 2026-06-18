import requests
from src.types import Endereco

def get_endereco_by_cep(cep: str) -> Endereco | None:

    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:
        response = requests.get(url, timeout=5)
        print(f"VIA CEP RESPONSE: {response}\n")

    except requests.RequestException:
        return None
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    print(f"RESPONSE.JSON: {data}\n")

    if data.get("erro"):
        return None
    
    return Endereco(
        logradouro=data["logradouro"],
        bairro=data["bairro"],
        cidade=data["localidade"],
        uf=data["uf"],
        cep=cep,
    )