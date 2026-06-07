from dataclasses import dataclass

@dataclass
class IncomingMessage:
    #MENSAGEM RECEBIDA E NORMALIZADA

    msg_id: str
    phone: str
    name: str
    tipo: str
    timestamp: int
    text: str | None
    id_botao: str | None

    def is_duplicate(self, processed_ids: set[str]) -> bool:
        return self.msg_id in processed_ids