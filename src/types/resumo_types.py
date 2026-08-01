from dataclasses import dataclass, fields, is_dataclass, field
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

    def to_str(self, sep: str = "\n") -> str:
        rows = []
        for f in fields(cast(IsDataclass, self)):
            v = getattr(self, f.name)
            if v is None or f.metadata.get("oculto"):
                continue

            label = f.metadata.get("label", f.name)
            rows.append(f"{label}: {v}")

        return sep.join(rows)

@dataclass
class MsgResumo(ResumoMixin):
    role:    str | None = field(default=None, metadata={"label": "De"})
    content: str | None = field(default=None, metadata={"label": "Mensagem"})

@dataclass
class StatusResumo(ResumoMixin):
    status:            str | None = field(default=None, metadata={"label": "Status"})
    erro_msg:          str | None = field(default=None, metadata={"label": "Erro"})
    created_at:        str | None = field(default=None, metadata={"label": "Criado em"})
    updated_at:        str | None = field(default=None, metadata={"label": "Atualizado em"})
    invoice_id:        str | None = field(default=None, metadata={"label": "Nota fiscal"})
    draft_json:        str | None = field(default=None, metadata={"oculto": True})
    requested_at:      str | None = field(default=None, metadata={"label": "Solicitado em"})
    cancelled_at:      str | None = field(default=None, metadata={"label": "Cancelado em"})
    emitido_em:        str | None = field(default=None, metadata={"label": "Emitido em"})

@dataclass
class HistoryResumo(ResumoMixin):
    id:                int | None = field(default=None, metadata={"oculto": True})
    status:            str | None = field(default=None, metadata={"label": "Status"})
    conv_id:           int | None = field(default=None, metadata={"oculto": True})
    tentativas:        int | None = field(default=None, metadata={"label": "Tentativas"})
    nome:              str | None = field(default=None, metadata={"label": "Tomador"})
    cnpj:              str | None = field(default=None, metadata={"label": "CNPJ"})
    descricao_servico: str | None = field(default=None, metadata={"label": "Serviço"})
    valor_total:       str | None = field(default=None, metadata={"label": "Valor"})
    requested_at:      str | None = field(default=None, metadata={"label": "Solicitado em"})
    created_at:        str | None = field(default=None, metadata={"label": "Criado em"})
    invoice_id:        str | None = field(default=None, metadata={"label": "Nota fiscal"})
    emitido_em:        str | None = field(default=None, metadata={"label": "Emitido em"})
    issued_at:         str | None = field(default=None, metadata={"label": "Emitido em (API)"})
    erro_code:         str | None = field(default=None, metadata={"oculto": True})
    erro_msg:          str | None = field(default=None, metadata={"label": "Erro"})
    cancelled_at:      str | None = field(default=None, metadata={"label": "Cancelado em"})