import requests


def get_cnpj_info(cnpj: str) -> dict | None:

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

    try:
        response = requests.get(url, timeout=5)
        print(f"BRASILAPI CNPJ RESPONSE: {response}\n")

    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    print(f"RESPONSE.JSON: {data}\n")

    return data
