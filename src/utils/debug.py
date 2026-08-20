import logging

from src.database.db import DB

logger = logging.getLogger(__name__)


def log_table(
    table_name: str,
    columns: list[str] | None = None,
    where: str | None = None,
    params: tuple = (),
    limit: int | None = None,
    max_width: int = 80,
) -> None:
    """
    Loga o conteúdo de uma tabela, com tratamento para campos longos (como JSON).
    Debug interno — vai para o logger (sujeito à redação de CPF/CNPJ/valores em
    src/logging_config.py), nunca para o usuário.
    """
    db = DB()
    col_str = ", ".join(columns) if columns else "*"
    query = f"SELECT {col_str} FROM {table_name}"

    if where:
        query += f" WHERE {where}"
    if limit:
        query += f" LIMIT {limit}"

    rows = db.fetchall(query, params)

    if not rows:
        logger.debug("Tabela '%s' está vazia.", table_name)
        return

    col_names = columns if columns else list(rows[0].keys())

    col_widths = {col: len(col) for col in col_names}

    for row in rows:
        for col in col_names:
            value = str(row[col])
            if len(value) > max_width:
                value = value[:max_width - 3] + "..."
            col_widths[col] = max(col_widths[col], len(value))

    for col in col_names:
        col_widths[col] = min(col_widths[col], max_width)

    header = " | ".join(col.ljust(col_widths[col]) for col in col_names)
    separator = "-+-".join("-" * col_widths[col] for col in col_names)

    lines = [f"Tabela: {table_name.upper()}", header, separator]

    for row in rows:
        line_parts = []
        for col in col_names:
            value = str(row[col])
            if len(value) > max_width:
                value = value[:max_width - 3] + "..."
            line_parts.append(str(value).ljust(col_widths[col]))
        lines.append(" | ".join(line_parts))

    lines.append(f"Total de registros: {len(rows)}")
    logger.debug("\n".join(lines))
