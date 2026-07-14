from dataclasses import dataclass, field, fields, is_dataclass
from typing import Generic, Protocol, TypeVar, Any, Self, ClassVar
from src.types.user import User
from src.types.wpp_msg import MsgType

#------------------------------- CONTEXT BASE -------------------------------#

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

#------------------------------- CONTEXT PRESTADOR -------------------------------#

@dataclass
class PrestadorData:
    razao_social:      str | None = None
    cnpj:              str | None = None
    email:             str | None = None
    regime_tributario: str | None = None
    cep:               str | None = None 
    address:           Address | None = None

    OBRIGATORIOS: ClassVar[set[str]] = {
        "razao_social", "cnpj", "email", "regime_tributario", "cep"
    }

    def merge(self, novos: "PrestadorData") -> "PrestadorData":
        campos = [f.name for f in fields(self)]
        kwargs = {}

        for c in campos:
            valor_novo = getattr(novos, c)
            valor_atual = getattr(self, c)

            if is_dataclass(valor_novo) and is_dataclass(valor_atual):
                kwargs[c] = valor_atual.merge(valor_novo)
            else:
                kwargs[c] = valor_novo if valor_novo is not None else valor_atual

        return PrestadorData(**kwargs)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PrestadorData":
        if not data:
            return cls()
        
        campos_endereco = {f.name for f in fields(Address)}
        endereco_data = {k: data.get(k) for k in campos_endereco if k in data}
        endereco = Address(**endereco_data) if any(v is not None for v in endereco_data.values()) else None

        campos_diretos = {f.name for f in fields(cls)} - {"endereco"}
        kwargs = {f: data.get(f) for f in campos_diretos}
        kwargs["endereco"] = endereco

        return cls(**kwargs)
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
    def is_complete(self) -> bool:
        return not self.campos_faltantes()

@dataclass
class ContextPrestador(ContextBase[PrestadorData]):
    conversation_id: int | None = None
    idempotency_key: str = ""

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

@dataclass
class ResultadoOnboarding:
    sucesso:    bool
    project_id: str | None = None
    api_key:    str | None = None
    erro:       str | None = None

@dataclass
class ProjectPrestador:
    name: str
    cnpj: str
    razaoSocial: str
    inscricaoMunicipal: str
    regimeTributario: str
    email: str
    endereco: Address
    notaas_project_id: str
    notaas_api_key: str
    certificado_enviado: int
    onboarding_status: str
    created_at: str
    updated_at: str
    codigoMunicipio: str = "3304557"

#------------------------------- CONTEXT TOMADOR -------------------------------#

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
    nome: str | None = None
    cnpj: str | None = None

    OBRIGATORIOS: ClassVar[set[str]] = {"nome", "cnpj"}
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tomador":
        return cls(
            nome=data.get("nome"),
            cnpj=data.get("cnpj"),
        )

    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class Servico(MergeableMixin):
    descricao: str | None = None

    OBRIGATORIOS: ClassVar[set[str]] = {"descricao"}
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Servico":
        return cls(descricao=data.get("descricao"))

    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class Valores(MergeableMixin):
    total:       float | None = None
    aliquotaIss: float | None = None

    OBRIGATORIOS: ClassVar[set[str]] = {"total"}
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Valores":
        return cls(
            total=data.get("total"),
            aliquotaIss=data.get("aliquotaIss"),
        )

    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
@dataclass
class TomadorData:
    tomador: Tomador = field(default_factory=Tomador)
    servico: Servico = field(default_factory=Servico)
    valores: Valores = field(default_factory=Valores)

    def merge(self, novos: "TomadorData") -> "TomadorData":
        return TomadorData(
            tomador=self.tomador.merge(novos.tomador),
            servico=self.servico.merge(novos.servico),
            valores=self.valores.merge(novos.valores),
        )
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TomadorData":
        return cls(
            tomador=Tomador.from_dict(data.get("tomador") or {}),
            servico=Servico.from_dict(data.get("servico") or {}),
            valores=Valores.from_dict(data.get("valores") or {}),
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
class ContextTomador(ContextBase[TomadorData]):
    conversation_id: int | None = None
    idempotency_key: str = ""
    conv_status:     str | None = None