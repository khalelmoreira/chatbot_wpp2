from src.database.db import DB
from src.types import IssRate


class IssRateManager:
    """Acesso à tabela iss_rates. Sem HTTP — só DB."""

    def __init__(self):
        self.db = DB()

    def upsert_rates(self, rows: list[IssRate]) -> None:
        for row in rows:
            self._upsert_rate(row)

    # SQL explícito: upsert por chave composta (codigo_municipio, codigo_tributacao_nacional,
    # vigencia_inicio) — insert()/update() genéricos não expressam ON CONFLICT.
    def _upsert_rate(self, row: IssRate) -> None:
        self.db.exe("""
            INSERT INTO iss_rates (
                codigo_municipio, codigo_tributacao_nacional,
                aliquota, vigencia_inicio, vigencia_fim, updated_at
            )
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT (codigo_municipio, codigo_tributacao_nacional, vigencia_inicio) DO UPDATE SET
                aliquota     = excluded.aliquota,
                vigencia_fim = excluded.vigencia_fim,
                updated_at   = excluded.updated_at
        """, (
            row.codigo_municipio, row.codigo_tributacao_nacional,
            row.aliquota, row.vigencia_inicio, row.vigencia_fim,
        ))

    # SQL explícito: janela de vigência (vigencia_inicio <= hoje <= vigencia_fim OU vigencia_fim
    # NULL) não é expressável pelo select() genérico (só faz igualdade em AND).
    def get_current_rate(self, codigo_municipio: str, codigo_tributacao_nacional: str) -> IssRate | None:
        row = self.db.fetchone("""
            SELECT codigo_municipio, codigo_tributacao_nacional, aliquota, vigencia_inicio, vigencia_fim
            FROM iss_rates
            WHERE codigo_municipio = ?
              AND codigo_tributacao_nacional = ?
              AND vigencia_inicio <= DATE('now')
              AND (vigencia_fim IS NULL OR vigencia_fim >= DATE('now'))
            ORDER BY vigencia_inicio DESC
            LIMIT 1
        """, (codigo_municipio, codigo_tributacao_nacional))

        if row is None:
            return None

        return IssRate(
            codigo_municipio=row["codigo_municipio"],
            codigo_tributacao_nacional=row["codigo_tributacao_nacional"],
            aliquota=row["aliquota"],
            vigencia_inicio=row["vigencia_inicio"],
            vigencia_fim=row["vigencia_fim"],
        )
