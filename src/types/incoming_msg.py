from dataclasses import dataclass

@dataclass
class IncomingMessage:
    #MENSAGEM RECEBIDA E NORMALIZADA

    msg_id: str
    phone: str
    contact_name: str
    text: str
    timestamp: int
    tipo: str

    def is_duplicate(self, processed_ids: set[str]) -> bool:
        return self.msg_id in processed_ids