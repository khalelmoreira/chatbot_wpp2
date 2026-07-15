from dataclasses import dataclass, field, fields
from typing import Any, Self, ClassVar, cast
from enum import StrEnum
from src.types.base import ContextBase, Address

@dataclass
class MergeableMixin:
    def merge(self, novos: "Self") -> "Self":
        kwargs = {
            f.name: getattr(novos, f.name) if getattr(novos, f.name) is not None else getattr(self, f.name)
            for f in fields(self)
        }
        return type(self)(**kwargs)

class DocTomadorType(StrEnum):
    CPF  = "CPF"
    CNPJ = "CNPJ"

@dataclass
class Doc:
    tipo:   DocTomadorType
    numero: str

    @classmethod
    def doc_from_dict(cls, data: dict[str, str | None]) -> "Doc":
        cpf = data.get("cpf")
        cnpj = data.get("cnpj")

        if cpf and cnpj:
            raise ValueError("Tomador com cpf e cnpj preenchidos simultaneamente")
        if not cpf and not cnpj:
            raise ValueError("Tomador sem cpf nem cnpj")
        
        if cpf:
            return cls(tipo=DocTomadorType.CPF, numero=cpf)
        return cls(tipo=DocTomadorType.CNPJ, numero=cnpj) # type: ignore[arg-type]

    def to_columns(self) -> dict[str, str | None]:
        if self.tipo == DocTomadorType.CPF:
            return {"cpf": self.numero, "cnpj": None}
        return {"cpf": None, "cnpj": self.numero}

@dataclass
class TomadorT:
    id:           int
    prestador_id: int
    doc:          Doc

    nome:         str | None = None
    email:        str | None = None
    phone:        str | None = None
            
    cep:          str | None = None
    address:      Address | None = None

    created_at:   str | None = None
    updated_at:   str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "TomadorT":
        if not data or "id" not in data or "prestador_id" not in data:
            raise ValueError("TomadorT.from_dict requer 'id' e 'prestador_id' presente nos dados.")
        
        cols_address = {f.name for f in fields(Address)}
        address_data = {k: data.get(k) for k in cols_address if k in data}
        address = Address(**address_data) if any(v is not None for v in address_data.values()) else None

        direct_cols = {f.name for f in fields(cls)} - {"address", "id", "prestador_id", "doc"}
        kwargs = {f: data.get(f) for f in direct_cols}

        return cls(
            id=data["id"],
            prestador_id=data["prestador_id"],
            doc=Doc.doc_from_dict(data),
            address=address,
            **kwargs,
        )


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