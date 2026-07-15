from dataclasses import dataclass, field, fields
from typing import Generic, Protocol, TypeVar, Self, Any
from enum import StrEnum
from src.types.wpp_msg import MsgType

class UserStatus(StrEnum):
    COLLECTING  = "COLLECTING"
    ADDRESS     = "ADDRESS"
    CONFIRMING  = "CONFIRMING"
    PROJECT     = "PROJECT"
    CERTIFICATE = "CERTIFICATE"
    ACTIVE      = "ACTIVE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

@dataclass
class User:
    id:     int
    phone:  str
    name:   str | None = None
    status: UserStatus | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User | None":
        if not data or "id" not in data or "phone" not in data:
            return None
        return cls(
            id=data["id"],
            phone=data["phone"],
            name=data.get("name"),
            status=UserStatus(data["status"]) if data.get("status") else None
        )

@dataclass
class Address:
    logradouro:  str | None = None
    bairro:      str | None = None
    cidade:      str | None = None
    uf:          str | None = None
    numero:      str | None = None
    complemento: str | None = None

    def merge(self, novos: "Address") -> "Address":
        campos = [f.name for f in fields(self)]
        kwargs = {
            c: getattr(novos, c) if getattr(novos, c) is not None else getattr(self, c)
            for c in campos
        }
        return Address(**kwargs)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Address":
        if not data:
            return cls()
        
        cols = {f.name for f in fields(cls)}
        kwargs = {f: data.get(f) for f in cols if f in data}
        return cls(**kwargs)

class Mergeable(Protocol):
    def merge(self, novos: Self) -> Self: ...

T = TypeVar("T", bound=Mergeable)

@dataclass
class ValidationResult:
    valid:   dict[str, object] = field(default_factory=dict)
    invalid: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.missing

@dataclass
class ContextBase(Generic[T]):
    user:       User
    text:       str
    new_data:   T
    db_data:    T
    merged:     T
    validated:  T
    msg_type:   MsgType
    button_id:  str | None = None
    validation: ValidationResult = field(default_factory=ValidationResult)