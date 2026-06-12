from typing import Optional, ClassVar
from dataclasses import dataclass, field, fields
from src.types.context_base import ContextBase

@dataclass
class Tomador:
    nome: Optional[str] = None
    cnpj: Optional[str] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"nome", "cnpj"}

    def merge(self, novos: "Tomador") -> "Tomador":

        kwargs = {
            f.name: getattr(novos, f.name) if getattr(novos, f.name) is not None else getattr(self, f.name)
            for f in fields(self)
        }

        return Tomador(**kwargs)
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class Servico:
    descricao: Optional[str] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"descricao"}

    def merge(self, novos: "Servico") -> "Servico":

        kwargs = {
            f.name: getattr(novos, f.name) if getattr(novos, f.name) is not None else getattr(self, f.name)
            for f in fields(self)
        }
        return Servico(**kwargs)
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]

@dataclass
class Valores:
    total: Optional[float] = None
    aliquotaIss: Optional[float] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"total"}

    def merge(self, novos: "Valores") -> "Valores":
        kwargs = {
            f.name: getattr(novos, f.name) if getattr(novos, f.name) is not None else getattr(self, f.name)
            for f in fields(self)
        }
        return Valores(**kwargs)
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class DadosTomador:
    tomador: Tomador = field(default_factory=Tomador)
    servico: Servico = field(default_factory=Servico)
    valores: Valores = field(default_factory=Valores)

    def merge(self, novos: "DadosTomador") -> "DadosTomador":
        return DadosTomador(
            tomador=self.tomador.merge(novos.tomador),
            servico=self.servico.merge(novos.servico),
            valores=self.valores.merge(novos.valores),
        )
    
    def campos_faltantes(self) -> list[str]:
        return (
            [f"tomador.{c}" for c in self.tomador.campos_faltantes()] +
            [f"servico.{c}" for c in self.servico.campos_faltantes()] +
            [f"valores.{c}" for c in self.valores.campos_faltantes()]
        )
    
    def is_complete(self) -> bool:
        return not self.campos_faltantes()
    
@dataclass
class ContextTomador(ContextBase[DadosTomador]):
    conversation_id: int | None = None
    idempotency_key: str = ""