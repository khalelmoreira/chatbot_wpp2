import requests
import os

API_KEY = os.getenv("NOTAAS_API_KEY")


def emitir_nf(dados):

    print(f"\n\n----------------TESTE EMITIR NF----------------\n\n")

    url = "https://platform.notaas.com.br/api/v1/emitir"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    response = requests.post(url, json=dados, headers=headers)
    print(f"RESPONSE: {response}\n")
    print(f"RESPONSE.json: {response.json()}\n")

    if response.status_code not in [200, 201, 202]:
        raise Exception(f"Erro na emissão: {response.text}")
    
    return response.json()
