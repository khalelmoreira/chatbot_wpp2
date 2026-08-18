from dataclasses import dataclass, field

from src.types.mixins import TextMixin


@dataclass
class MsgResumo(TextMixin):
    role:    str | None = field(default=None, metadata={"label": "De"})
    content: str | None = field(default=None, metadata={"label": "Mensagem"})

@dataclass
class StatusResumo(TextMixin):
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
class HistoryResumo(TextMixin):
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