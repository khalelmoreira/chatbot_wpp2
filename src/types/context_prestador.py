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
    numero: str
    bairro: str
    cidade: str
    uf: str
    complemento: str | None = None

@dataclass
class ResultadoOnboarding:
    sucesso: bool
    project_id: str | None = None
    api_key: str | None = None
    erro: str | None = None

    
# @dataclass
# class DadosPrestador:

#     razao_social: str | None = None
#     cnpj: str | None = None
#     email: str | None = None
#     inscricao_municipal: str | None = None
#     regime_tributario: str | None = None
#     cep: str | None = None

#     razaoSocial: str
#     cnpj: str
#     email: str
#     codigoMunicipio: str = "3304557"

#     inscricaoMunicipal: str | None = None
#     inscricaoEstadual: str | None = None
#     regimeTributario: str | None = None

#     endereco: Endereco

#     phone: str | None

#     notaas_project_id: str | None
#     notaas_api_key: str | None
#     certificado_enviado: bool

#     onboarding_status: str
#     created_at: datetime

