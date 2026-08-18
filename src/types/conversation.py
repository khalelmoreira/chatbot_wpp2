import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ConvStatus(StrEnum):
    COLLECTING  = "COLLECTING"
    CONFIRMING  = "CONFIRMING"
    QUEUED      = "QUEUED"
    DONE        = "DONE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class IntentType(StrEnum):
    EMITIR   = "EMITIR"
    CONSULTA = "CONSULTA"
    NENHUM   = "NENHUM"

@dataclass
class ResultExtract:
    campos: dict
    parece_pergunta: bool

@dataclass
class Conversation:
    id:                 int
    prestador_id:       int
    phone:              str
    status:             ConvStatus
    draft_json:         dict[str, Any] = field(default_factory=dict)

    created_at:         str | None = None
    updated_at:         str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Conversation":
        if not data or "id" not in data or "prestador_id" not in data or "phone" not in data:
            raise ValueError("Conversation.from_dict requer 'id', 'prestador_id' e 'phone' presentes nos dados.")
        
        raw_draft = data.get("draft_json") or "{}"
        draft = json.loads(raw_draft) if isinstance(raw_draft, str) else raw_draft

        return cls(
            id=data["id"],
            prestador_id=data["prestador_id"],
            phone=data["phone"],
            status=ConvStatus(data["status"]),
            draft_json=draft,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    def to_columns(self) -> dict[str, Any]:
        return {
            "prestador_id": self.prestador_id,
            "phone":        self.phone,
            "status":       self.status.value,
            "draft_json":   json.dumps(self.draft_json),
        }