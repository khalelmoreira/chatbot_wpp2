import logging
import os
from collections.abc import Sequence

import requests
from dotenv import load_dotenv

from src.types import BotaoResponse

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramService:

    def _post_telegram(self, method: str, payload: dict) -> dict | None:

        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/{method}"

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.debug("mensagem enviada com sucesso")

                return response.json()

            logger.error("erro ao enviar mensagem: %s - %s", response.status_code, response.text)

            return None

        except requests.RequestException:
            logger.exception("erro no request ao enviar mensagem")

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
            "chat_id": phone,
            "text": text,
        }

        return self._post_telegram("sendMessage", payload)

    def send_msg_botao(
            self,
            phone: str,
            text: str,
            botoes: list[BotaoResponse],
            rodape: str | None = None
    ) -> dict | None:

        if not (1 <= len(botoes) <= 3):
            raise ValueError(f"telegram (uso deste bot) aceita entre 1 e 3 botoes, recebido: {len(botoes)}")

        if rodape:
            text = f"{text}\n\n{rodape}"

        payload = {
            "chat_id": phone,
            "text": text,
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": b.title, "callback_data": b.id} for b in botoes]
                ]
            },
        }

        return self._post_telegram("sendMessage", payload)

    def responder_callback(self, callback_query_id: str) -> dict | None:
        """Telegram exige um `answerCallbackQuery` pra tirar o spinner de
        carregando do botão tocado pelo usuário — sem WhatsApp equivalente."""

        return self._post_telegram("answerCallbackQuery", {"callback_query_id": callback_query_id})

    def format_msg_botao(self, text: str, botoes: list[BotaoResponse]) -> str:
        opcoes = " / ".join(f"[{b.title}]" for b in botoes)
        conteudo = f"{text}\n\nOpções: {opcoes}"
        return conteudo

    def formatar_lista(self, lista: Sequence[str]) -> str:
        return "\n".join(f"- {item}" for item in lista)
