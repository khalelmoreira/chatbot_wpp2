import requests
import os
from collections.abc import Sequence
from dotenv import load_dotenv
from src.types import Endereco, BotaoResponse

load_dotenv()

class WhatsAppService:

    def _post_wpp(self, payload: dict) -> dict | None:

        url = (
            f"https://graph.facebook.com"
            f"/{os.getenv('API_META_VERSION')}"
            f"/{os.getenv('PHONE_NUMBER_ID_TEST_META')}/messages"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code in (200, 201):
                print("mensagem enviada com sucesso\n")

                return response.json()
            
            print(f"erro ao enviar mensagem: {response.status_code} - {response.text}")

            return None
        
        except requests.RequestException as e:
            print(f"erro no request: {e}")

            return None

    def send_msg_text(
            self,
            phone: str,
            text: str,
            lista: Sequence[str] | None = None
        ) -> dict | None:

        if lista:
            text = f"{text}\n{self.formatar_lista(lista)}"

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"body": text},
        }

        return self._post_wpp(payload)

    def send_msg_botao(
            self,
            phone: str,
            text: str,
            botoes: list[BotaoResponse],
            rodape: str | None = None
    ) -> dict | None:
        
        if not (1 <= len(botoes) <= 3):
            raise ValueError(f"whatsapp aceita entre 1 e 3 botoes, recebido: {len(botoes)}")

        interactive: dict = {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b.id, "title": b.title}}
                    for b in botoes
                ]
            },
        }

        if rodape:
            interactive["footer"] = {"text": rodape}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive,
        }

        return self._post_wpp(payload)

    def msg_build_endereco(phone: str, endereco: Endereco) -> dict:

        rows = [
            f"📍 *Endereço encontrado:*",
            f"",
            f"{endereco.logradouro}",
            f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}",
            f"CEP: {endereco.cep}",
            f"",
            f"Esse é o seu endereço?",
        ]

        return {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "\n".join(rows)
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "endereco_confirmado",
                                "title": "✅ Sim, confirmar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "endereco_corrigir",
                                "title": "✏️ Corrigir"
                            }
                        }
                    ]
                }
            }
        }

    def formatar_lista(lista: Sequence[str]) -> str:
        return "\n".join(f"- {item}" for item in lista)