from typing import Optional
from dataclasses import dataclass, fields
from typing import ClassVar
from src.types.context_base import ContextBase

@dataclass
class DadosPrestador:
    razao_social:      Optional[str] = None  # razaoSocial no Notaas
    cnpj:              Optional[str] = None
    email:             Optional[str] = None
    regime_tributario: Optional[str] = None  # "1"|"2"|"3"|"3e"
    cep:               Optional[str] = None 

    inscricao_municipal: Optional[str] = None

    OBRIGATORIOS: ClassVar[set[str]] = {
        "razao_social", "cnpj", "email", "regime_tributario", "cep"
    }

    def merge(self, novos: "DadosPrestador") -> "DadosPrestador":
        campos = [f.name for f in fields(self)]
        kwargs = {
            c: getattr(novos, c) if getattr(novos, c) is not None else getattr(self, c) for c in campos
        }

        return DadosPrestador(**kwargs)
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
    def is_complete(self) -> bool:
        return not self.campos_faltantes()
    
ContextPrestador = ContextBase[DadosPrestador]

@dataclass
class Endereco:
    logradouro: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    numero: Optional[str] = None
    complemento: Optional[str]  = None

@dataclass
class ResultadoOnboarding:
    sucesso: bool
    project_id: str | None = None
    api_key: str | None = None
    erro: str | None = None

