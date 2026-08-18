from typing import Any, ClassVar, Protocol, Self, runtime_checkable


@runtime_checkable
class Mergeable(Protocol):
    def merge(self, novos: Self) -> Self: ...

class FromDictable(Protocol):
    @classmethod
    def from_dict(cls, data: dict) -> Self: ...

class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]