import logging

from src.services.ai.audio_service import transcrever_audio_telegram
from src.types import IncomingMessage, MsgType

logger = logging.getLogger(__name__)

class TelegramParser:
    def __init__(self, payload):
        self.payload = payload

    def parse(self) -> IncomingMessage | None:

        callback_query = self.payload.get("callback_query")
        if callback_query is not None:
            return self._parse_callback_query(callback_query)

        message = self.payload.get("message")
        if message is None:
            return None

        chat = message.get("chat", {})
        phone = str(chat["id"])
        msg_id = str(message["message_id"])
        timestamp = int(message["date"])
        name = message.get("from", {}).get("first_name", "")

        if "text" in message:
            return IncomingMessage(
                msg_id=msg_id,
                phone=phone,
                name=name,
                tipo=MsgType.TEXT,
                timestamp=timestamp,
                text=message["text"],
                channel="TELEGRAM",
            )

        voice = message.get("voice") or message.get("audio")
        if voice is not None:
            return IncomingMessage(
                msg_id=msg_id,
                phone=phone,
                name=name,
                tipo=MsgType.AUDIO,
                timestamp=timestamp,
                text=transcrever_audio_telegram(voice["file_id"]),
                channel="TELEGRAM",
            )

        logger.warning("tipo de mensagem do telegram nao tratado: %s", list(message.keys()))
        return None

    def _parse_callback_query(self, callback_query: dict) -> IncomingMessage | None:
        message = callback_query.get("message", {})
        chat = message.get("chat", {})
        phone = chat.get("id")
        if phone is None:
            logger.warning("callback_query sem chat associado: %s", callback_query)
            return None

        return IncomingMessage(
            msg_id=str(callback_query["id"]),
            phone=str(phone),
            name=callback_query.get("from", {}).get("first_name", ""),
            tipo=MsgType.BUTTON,
            timestamp=int(message.get("date", 0)),
            text="",
            button_id=callback_query["data"],
            channel="TELEGRAM",
        )
