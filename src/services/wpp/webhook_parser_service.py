from typing import Optional
from src.types import IncomingMessage
from src.services.shared.audio_service import transcrever_audio_wpp

class WhatsappWebhookParser:
    def __init__(self, payload):
        self.payload = payload

    def parse(self) -> Optional[IncomingMessage]:

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
                tipo="text",
                timestamp=timestamp,
                text=message["text"]["body"],
                id_botao=None,
            )

        if tipo_raw == "audio":

            return IncomingMessage(
                msg_id=msg_id,
                phone=phone,
                name=name,
                tipo="audio",
                timestamp=timestamp,
                text = transcrever_audio_wpp(msg_id),
                id_botao=None,
            )
            
        if tipo_raw == "interactive":
            subtipo = message["interactive"].get("type")

            if subtipo == "button_reply":

                button_reply = message["interactive"]["button_reply"]

                return IncomingMessage(
                    msg_id=msg_id,
                    phone=phone,
                    name=name,
                    tipo="button_reply",
                    timestamp=timestamp,
                    text=None,
                    id_botao=button_reply["id"]
                )
            
            print(f"subtipo interativo nao tratado: {subtipo}")
            return None

        else:
            print(f"tipo não tratado: {tipo_raw}")
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