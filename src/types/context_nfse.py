from typing import Optional
from dataclasses import dataclass, field
from src.types.context_base import ContextBase

@dataclass
class Tomador:
    nome: Optional[str] = None
    cnpj: Optional[str] = None

    def merge(self, novos: "Tomador") -> "Tomador":
        return Tomador(
            nome=novos.nome or self.nome,
            cnpj=novos.cnpj or self.cnpj,
        )
    
    def campos_faltantes(self) -> list[str]:
        return [k for k, v in vars(self).items() if v is None]
    
@dataclass
class Servico:
    descricao: Optional[str] = None

    def merge(self, novos: "Servico") -> "Servico":
        return Servico(descricao=novos.descricao or self.descricao)
    
    def campos_faltantes(self) -> list[str]:
        return [k for k, v in vars(self).items() if v is None]

@dataclass
class Valores:
    total: Optional[float] = None
    aliquotaIss: Optional[float] = None

    def merge(self, novos: "Valores") -> "Valores":
        return Valores(
            total=novos.total or self.total,
            aliquotaIss=novos.aliquotaIss or self.aliquotaIss,
        )
    
    def campos_faltantes(self) -> list[str]:
        return [k for k, v in vars(self).items() if v is None]
    
@dataclass
class DadosNfse:
    tomador: Tomador = field(default_factory=Tomador)
    servico: Servico = field(default_factory=Servico)
    valores: Valores = field(default_factory=Valores)

    def merge(self, novos: "DadosNfse") -> "DadosNfse":
        return DadosNfse(
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
    
ContextNfse = ContextBase[DadosNfse]