from dataclasses import dataclass, field
from typing import Generic, Optional, Protocol, TypeVar, Literal, Any

EstadoUser = Literal["novo", "ativo", "aguardando_dados"]

class Merge(Protocol):
    def merge(self: "T", novos: "T") -> "T":...
    def is_complete(self) -> bool:...
    def campos_faltantes(self) -> list[str]:...

T = TypeVar("T", bound=Merge)

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
    def is_valido(self) -> bool:
        return not self.invalidos and not self.faltantes

@dataclass
class ContextBase(Generic[T]):
    user: User
    text: str
    dados_novos: T
    dados_db: T
    dados_normalizados: Optional[T] = None
    validacao: ResultadoValidacao = field(default_factory=ResultadoValidacao)

    @property
    def dados_completos(self) -> T:
        return self.dados_db.merge(self.dados_novos)
    
    @property
    def completo(self) -> bool:
        return self.dados_completos.is_complete()
    
    @property
    def campos_faltantes(self) -> list[str]:
        return self.dados_completos.campos_faltantes()
