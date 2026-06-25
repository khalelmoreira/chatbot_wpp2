from dataclasses import dataclass
from typing import Protocol, TypedDict, Literal
from enum import Enum

# ─── Contrato da IA ──────────────────────────────────────────────────────────
# StateMachine não sabe como a IA funciona — só o que ela precisa receber e retornar

@dataclass
class AIResponse:
    message: str                   # texto para o usuário
    extraido: dict                 # dados novos identificados nesta mensagem
    intencao: bool = False         # intenção de emissao, ia detecta

class AIClient(Protocol):
    def process(self, history: list[dict], draft: dict, state: str) -> AIResponse:...

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
    
#PAYLOAD RAW

TypeMessage = Literal [
    "text",
    "image",
    "audio",
    "document",
    "video",
    "reaction",
    "button"
]

class TextMessageDict(TypedDict):
    body: str

class MessageDict(TypedDict, total=False):
    id: str
    timestamp: str
    type: TypeMessage
    text: TextMessageDict
    audio_id: str

class ProfileDict(TypedDict):
    name: str

class ContactDict(TypedDict):
    wa_id: str
    profile: ProfileDict

class ValueDict(TypedDict, total=False):
    contacts: list[ContactDict]
    messages: list[MessageDict]

class WebhookPayload(TypedDict):
    entry: list[dict]

@dataclass
class BotaoResponse:
    id: str
    title: str

class Role(str, Enum):
    USER = "USER"
    AI   = "AI"

@dataclass
class MessageType:
    conversation_id: int
    role: Role
    content: str
    created_at: str