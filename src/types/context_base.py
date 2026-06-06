from dataclasses import dataclass, field
from typing import Generic, Optional, Protocol, TypeVar, Literal, Any, Self

EstadoUser = Literal[
    "novo",
    "cadastro_prestador",
    "ativo"
]

class Mergeable(Protocol):
    def merge(self, novos: Self) -> Self: ...

T = TypeVar("T", bound=Mergeable)

@dataclass
class User:
    id: int
    phone: str
    estado: EstadoUser

@dataclass
class ResultadoValidacao:
    validos: dict[str, Any] = field(default_factory=dict)
    invalidos: list[str] = field(default_factory=list)
    faltantes: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.invalidos and not self.faltantes

@dataclass
class ContextBase(Generic[T]):
    user: User
    text: str
    dados_novos: T
    dados_db: T
    dados_completos: T
    validacao: ResultadoValidacao = field(default_factory=ResultadoValidacao)
