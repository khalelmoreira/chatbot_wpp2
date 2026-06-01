import requests
import os
from typing import Literal
from collections.abc import Sequence
from dotenv import load_dotenv

load_dotenv()

TipoMensagem = Literal["text"]

def enviar_mensagem(
        phone: str,
        tipo: TipoMensagem,
        text: str,
        lista: Sequence[str] | None = None
    ) -> dict | None:

    if lista:
        text = f"{text}\n{formatar_lista(lista)}"

    url = f"https://graph.facebook.com/{os.getenv('API_META_VERSION')}/{os.getenv('PHONE_NUMBER_ID_TEST_META')}/messages"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": tipo,
        "text": {
            "body": text
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            print("Mensagem enviada com sucesso!\n")
            return response.json()
        
        print("Erro ao enviar a mensagem:\n")
        print(response.status_code)
        print(response.text)
        return None
        
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:\n", e)
        return None


def formatar_lista(lista: Sequence[str]) -> str:
    return "\n".join(f"- {item}" for item in lista)