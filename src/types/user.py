from operator import add
from typing import Any, ClassVar
from enum import StrEnum
from dataclasses import dataclass, fields, is_dataclass
from src.types.base import ContextBase, User, UserStatus, Address

class IntentUserType(StrEnum):
    ONBOARDING  = "ONBOARDING"
    ASK_PRICE   = "ASK_PRICE"
    ASK_WORKING = "ASK_WORKING"
    GENERAL_ASK = "GENERAL_ASK"
    NENHUM      = "NENHUM"


@dataclass
class Prestador:
    id:                  int
    phone:               str
    status:              UserStatus | None = None
    name:                str | None = None
    email:               str | None = None

    cnpj:                str | None = None
    razao_social:        str | None = None
    regime_tributario:   str | None = None

    cep:                 str | None = None
    address:             Address | None = None

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