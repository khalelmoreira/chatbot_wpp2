from dataclasses import dataclass, fields, is_dataclass
import sqlite3
from typing import Any, Mapping, Protocol, ClassVar, cast

class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]

class ResumoMixin:
    @classmethod
    def from_row(cls, data: Mapping[str, Any] | IsDataclass, **aliases: Any):
        if is_dataclass(data) and not isinstance(data, type):
            base = {f.name: getattr(data, f.name) for f in fields(data)}
        else:
            base = dict(cast(Mapping[str, Any], data))

        merged = {**base, **aliases}
        return cls(**{f.name: merged.get(f.name) for f in fields(cast(IsDataclass, cls))})

@dataclass
class MsgResumo(ResumoMixin):
    role:    str | None = None
    content: str | None = None

@dataclass
class StatusResumo(ResumoMixin):
    status:            str | None = None
    erro_msg:          str | None = None
    created_at:        str | None = None
    updated_at:        str | None = None
    invoice_id:        str | None = None
    draft_json:        str | None = None
    requested_at:      str | None = None
    cancelled_at:      str | None = None
    emitido_em:        str | None = None

@dataclass
class HistoryResumo(ResumoMixin):
    id:                int | None = None
    status:            str | None = None
    conv_id:           int | None = None
    tentativas:        int | None = None
    nome:              str | None = None
    cnpj:              str | None = None
    descricao_servico: str | None = None
    valor_total:       str | None = None
    requested_at:      str | None = None
    created_at:        str | None = None
    invoice_id:        str | None = None
    emitido_em:        str | None = None
    issued_at:         str | None = None
    erro_code:         str | None = None
    erro_msg:          str | None = None
    cancelled_at:      str | None = None