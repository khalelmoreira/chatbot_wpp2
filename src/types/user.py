from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any, ClassVar

from src.types.mixins import FromDictMixin, MergeableMixin, TextMixin


class UserStatus(StrEnum):
    COLLECTING  = "COLLECTING"
    ADDRESS     = "ADDRESS"
    CONFIRMING  = "CONFIRMING"
    PROJECT     = "PROJECT"
    CERTIFICATE = "CERTIFICATE"
    ACTIVE      = "ACTIVE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class IntentUserType(StrEnum):
    ONBOARDING  = "ONBOARDING"
    ASK_PRICE   = "ASK_PRICE"
    ASK_WORKING = "ASK_WORKING"
    GENERAL_ASK = "GENERAL_ASK"
    NENHUM      = "NENHUM"

@dataclass
class Address(MergeableMixin, FromDictMixin, TextMixin):
    logradouro:  str | None = None
    bairro:      str | None = None
    cidade:      str | None = None
    uf:          str | None = None
    numero:      str | None = None
    complemento: str | None = None

@dataclass(kw_only=True)
class User:
    id:     int
    phone:  str
    name:   str | None = None
    status: UserStatus | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User | None":
        if not data or "id" not in data or "phone" not in data:
            return None
        return cls(
            id=data["id"],
            phone=data["phone"],
            name=data.get("name"),
            status=UserStatus(data["status"]) if data.get("status") else None
        )

@dataclass(kw_only=True)
class PrestadorData(TextMixin, MergeableMixin):
    razao_social:      str | None = None
    cnpj:              str | None = None
    email:             str | None = None
    regime_tributario: str | None = None
    cep:               str | None = None 
    address:           Address | None = None

    OBRIGATORIOS: ClassVar[set[str]] = {
        "razao_social", "cnpj", "email", "regime_tributario", "cep"
    }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PrestadorData":
        if not data:
            return cls()
        
        campos_endereco = {f.name for f in fields(Address)}
        endereco_data = {k: data.get(k) for k in campos_endereco if k in data}
        endereco = Address(**endereco_data) if any(v is not None for v in endereco_data.values()) else None

        campos_diretos = {f.name for f in fields(cls)} - {"address"}
        kwargs = {f: data.get(f) for f in campos_diretos}
        kwargs["address"] = endereco

        return cls(**kwargs)
    
    @classmethod
    def from_prestador(cls, p: "Prestador") -> "PrestadorData":
        return cls(
            razao_social=p.razao_social,
            cnpj=p.cnpj,
            email=p.email,
            regime_tributario=p.regime_tributario,
            cep=p.cep,
            address=p.address,
        )
    
    def campos_faltantes(self) -> list[str]:
        return [c for c in self.OBRIGATORIOS if getattr(self, c) is None]
    
    def is_complete(self) -> bool:
        return not self.campos_faltantes()

@dataclass(kw_only=True)
class Prestador(PrestadorData, User):
    """Representa prestador table"""
    ntaas_project_id:    str | None = None
    ntaas_api_key:       str | None = None
    org_token:           str | None = None
    certificado_enviado: int | None = 0
    error_msg:           str | None = None
    created_at:          str | None = None
    updated_at:          str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Prestador":
        if not data or "id" not in data or "phone" not in data:
            raise ValueError("Prestador.from_dict requer 'id' e 'phone' presentes nos dados")
        
        cols_address = {f.name for f in fields(Address)}
        address_data = {k: data.get(k) for k in cols_address if k in data}
        address = Address(**address_data) if any(v is not None for v in address_data.values()) else None
        
        direct_cols = {f.name for f in fields(cls)} - {"address", "id", "phone", "status"}
        kwargs = {f: data.get(f) for f in direct_cols}

        return cls(
            id=data["id"],
            phone=data["phone"],
            status=UserStatus(data["status"]) if data.get("status") else None,
            address=address,
            **kwargs,
        )
        
    def as_user(self) -> "User":
        """View leve pra roteamento"""

        return User(
            id=self.id,
            phone=self.phone,
            name=self.name,
            status=self.status
        )