from dataclasses import dataclass
from enum import StrEnum
from typing import Any


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
    TOMADOR_CANCELAR     = "tomador_cancelar"

    ENDERECO_CONFIRMADO  = "endereco_confirmado"
    ENDERECO_CORRIGIR    = "endereco_corrigir"

    PRESTADOR_CONFIRMADO = "prestador_confirmado"
    PRESTADOR_CORRIGIR   = "prestador_corrigir"
    PRESTADOR_CANCELAR   = "prestador_cancelar"

class Role(StrEnum):
    USER = "USER"
    AI   = "AI"

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
    channel:   str = "WHATSAPP"

@dataclass
class BotaoResponse:
    id: str
    title: str

@dataclass
class MsgConvType:
    conv_id: int
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
        required = ("id", "prestador_id", "phone", "role", "content")
        if not data or any(field not in data for field in required):
            raise ValueError(
                "Message.from_dict requer 'id', 'prestador_id', 'phone', 'role', 'content' presente nos dados."
            )
        
        return cls(
            id=data["id"],
            prestador_id=data["prestador_id"],
            phone=data["phone"],
            role=Role(data["role"]),
            content=data["content"],
            created_at=data.get("created_at")
        )