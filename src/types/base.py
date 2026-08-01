from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar, Self, ClassVar, Any, runtime_checkable
from src.types.user import User
from src.types.wpp_msg import MsgType

T = TypeVar("T", bound=Mergeable)

@runtime_checkable
class Mergeable(Protocol):
    def merge(self, novos: Self) -> Self: ...

class FromDictable(Protocol):
    @classmethod
    def from_dict(cls, data: dict) -> Self: ...

class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]

@dataclass
class ValidationResult:
    invalid: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.missing
    
    @property
    def is_valid(self) -> bool:
        return not self.invalid

@dataclass
class ContextBase(Generic[T]):
    user:       User
    text:       str
    new_data:   T
    db_data:    T
    merged:     T
    valid:      T
    msg_type:   MsgType
    button_id:  str | None = None
    validation: ValidationResult = field(default_factory=ValidationResult)