from dataclasses import dataclass, field, fields
from typing import Generic, Protocol, TypeVar, Any, Self, ClassVar, Optional
from src.types.user import User

class Mergeable(Protocol):
    def merge(self, novos: Self) -> Self: ...

T = TypeVar("T", bound=Mergeable)

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

@dataclass
class ProjectPrestador:
    name: str
    cnpj: str
    razaoSocial: str
    inscricaoMunicipal: str
    regimeTributario: str
    email: str
    endereco: Endereco
    notaas_project_id: str
    notaas_api_key: str
    certificado_enviado: int
    onboarding_status: str
    created_at: str
    updated_at: str
    codigoMunicipio: str = "3304557"

@dataclass
class MergeableMixin:
    def merge(self, novos: "Self") -> "Self":
        kwargs = {
            f.name: getattr(novos, f.name) if getattr(novos, f.name) is not None else getattr(self, f.name)
            for f in fields(self)
        }
        return type(self)(**kwargs)

@dataclass
class Tomador(MergeableMixin):
    nome: Optional[str] = None
    cnpj: Optional[str] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"nome", "cnpj"}
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class Servico(MergeableMixin):
    descricao: Optional[str] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"descricao"}
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]

@dataclass
class Valores(MergeableMixin):
    total: Optional[float] = None
    aliquotaIss: Optional[float] = None

    OBRIGATORIOS: ClassVar[set[str]] = {"total"}
    
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
    conv_status: str | None = None