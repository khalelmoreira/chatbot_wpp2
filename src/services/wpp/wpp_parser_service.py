import logging

from src.services.ai.audio_service import transcrever_audio_wpp
from src.types import IncomingMessage, MsgType

logger = logging.getLogger(__name__)

class WppParser:
    def __init__(self, payload):
        self.payload = payload

    def parse(self) -> IncomingMessage | None:

        try:
            value = self._extrair_value()

        except (KeyError, IndexError) as e:
            raise ValueError(f"payload malformado: {e}") from e
        
        messages = value.get("messages", [])
        if not messages:
            return None
        
        contacts = value.get("contacts", [])
        name = (
            contacts[0]
            .get("profile", {})
            .get("name", "")
            if contacts else ""
        )
        
        message = messages[0]
        phone = message["from"]
        msg_id = message["id"]
        timestamp = int(message["timestamp"])
        tipo_raw = message.get("type")

        if tipo_raw == "text":
            
            return IncomingMessage(
                msg_id=msg_id,
                phone=phone,
                name=name,
                tipo=MsgType.TEXT,
                timestamp=timestamp,
                text=message["text"]["body"],
            )

        if tipo_raw == "audio":

            return IncomingMessage(
                msg_id=msg_id,
                phone=phone,
                name=name,
                tipo=MsgType.AUDIO,
                timestamp=timestamp,
                text = transcrever_audio_wpp(msg_id),
            )
            
        if tipo_raw == "interactive":
            subtipo = message["interactive"].get("type")

            if subtipo == "button_reply":

                button_reply = message["interactive"]["button_reply"]

                return IncomingMessage(
                    msg_id=msg_id,
                    phone=phone,
                    name=name,
                    tipo=MsgType.BUTTON,
                    timestamp=timestamp,
                    text="",
                    button_id=button_reply["id"]
                )
            
            logger.warning("subtipo interativo nao tratado: %s", subtipo)
            return None

        else:
            logger.warning("tipo nao tratado: %s", tipo_raw)
            #enviar_mensagem(message["from"], "text", "não entendi a mensagem.")
            return None
    
    def _extrair_value(self) -> dict:
        try:
            entry = self.payload["entry"][0]

            change = entry["changes"][0]

            return change["value"]
        except (KeyError, IndexError) as e:
            raise ValueError(
                f"campo ausente no payload: {e}"
                f"payload recebido: {self.payload}"
            ) from e 