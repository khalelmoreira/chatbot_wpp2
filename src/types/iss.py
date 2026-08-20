from dataclasses import dataclass


@dataclass(frozen=True)
class IssRate:
    codigo_municipio: str
    codigo_tributacao_nacional: str
    aliquota: float
    vigencia_inicio: str  # ISO date
    vigencia_fim: str | None = None


@dataclass(frozen=True)
class IssResolution:
    """Resultado de IssResolutionService.resolve(). `unclassified` e `codigo` são
    mutuamente exclusivos por construção — ver IssResolutionService."""

    unclassified: bool
    codigo_tributacao_nacional: str | None = None
    aliquota: float | None = None
