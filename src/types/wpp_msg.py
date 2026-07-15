from dataclasses import dataclass
from typing import Any, Protocol, TypedDict, Literal
from enum import StrEnum

@dataclass
class IncomingMessage:
    #MENSAGEM RECEBIDA E NORMALIZADA

    msg_id:    str
    phone:     str
    name:      str
    tipo:      MsgType
    timestamp: int
    text:      str
    button_id: str | None = None

    def is_duplicate(self, processed_ids: set[str]) -> bool:
        return self.msg_id in processed_ids
    
class MsgType(StrEnum):
    TEXT     = "text"
    IMAGE    = "image"
    AUDIO    = "audio"
    DOC      = "document"
    VIDEO    = "video"
    REACTION = "reaction"
    BUTTON   = "button"

class BotaoId(StrEnum):
    TOMADOR_CONFIRMADO   = "tomador_confirmado"
    TOMADOR_CORRIGIR     = "tomador_corrigir"

    ENDERECO_CONFIRMADO  = "endereco_confirmado"
    ENDERECO_CORRIGIR    = "endereco_corrigir"

    PRESTADOR_CONFIRMADO = "prestador_confirmado"
    PRESTADOR_CORRIGIR   = "prestador_corrigir"

@dataclass
class BotaoResponse:
    id: str
    title: str

class Role(StrEnum):
    USER = "USER"
    AI   = "AI"

@dataclass
class MsgConvType:
    conversation_id: int
    role: Role
    content: str
    created_at: str

@dataclass
class Message:
    id:             int
    prestador_id:   int
    phone:          str
    role:           Role
    content:        str
    created_at:     str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        if not data or "id" not in data or "prestador_id" not in data or "phone" not in data or "role" not in data or "content" not in data:
            raise ValueError("Message.from_dict requer 'id', 'prestador_id', 'phone', 'role', 'content' presente nos dados.")
        
        return cls(
            id=data["id"],
            prestador_id=data["prestador_id"],
            phone=data["phone"],
            role=Role(data["role"]),
            content=data["content"],
            created_at=data.get("created_at")
        )