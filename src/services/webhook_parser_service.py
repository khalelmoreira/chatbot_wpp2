from typing import Optional
from src.types.incoming_msg import IncomingMessage
from src.services.audio_service import transcrever_audio_wpp
from src.services.msg_service import enviar_mensagem

class WhatsappWebhookParser:

    def parse(self, payload: dict) -> Optional[IncomingMessage]:

        try:
            value = self.extrair_value(payload)

            print(f"value: {value}\n")

        except (KeyError, IndexError) as e:
            raise ValueError(f"payload malformado: {e}") from e
        
        messages = value.get("messages", [])
        if not messages:
            return None
        
        print(f"messages: {messages}\n")

        contacts = value.get("contacts", [])
        contact_name = (
            contacts[0]
            .get("profile", {})
            .get("name", "Desconhecido")
            if contacts else "Desconhecido"
        )
        
        print(f"contacts: {contacts}\n")

        message = messages[0]

        print(f"message: {message}\n")

        if message.get("type") == "text":

            tipo = message["type"]

            return IncomingMessage(
            msg_id=message["id"],
            phone=message["from"],
            contact_name=contact_name,
            text=message["text"]["body"],
            timestamp=int(message["timestamp"]),
            tipo=tipo
        )

        elif message.get("type") == "audio":
            
            tipo = message["type"]
            audio_id = message["id"]
            text = transcrever_audio_wpp(audio_id)

            return IncomingMessage(
            msg_id=audio_id,
            phone=message["from"],
            contact_name=contact_name,
            text=text,
            timestamp=int(message["timestamp"]),
            tipo=tipo
        )

        else:
            print("tipo não tratado\n")
            #enviar_mensagem(message["from"], "text", "não entendi a mensagem.")
            print("MSG: Não entendi a mensagem...\n")
            return None
    
    def extrair_value(self, payload: dict) -> dict:
        try:
            entry = payload["entry"][0]

            print(f"entry: {entry}\n")

            change = entry["changes"][0]

            print(f"change: {change}\n")

            return change["value"]
        except (KeyError, IndexError) as e:
            raise ValueError(
                f"campo ausente no payload: {e}"
                f"payload recebido: {payload}"
            ) from e 