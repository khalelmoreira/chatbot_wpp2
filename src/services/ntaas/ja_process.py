from src.database.get_connection import get_connection


def ja_process(
    delivery_id: str,
    *,
    event: str | None = None,
    invoice_id: str | None = None,
    payload_raw: bytes | str | None = None,
) -> bool:
    """Idempotência dos webhooks Notaas: insere a entrega e devolve True se ela já
    havia sido registrada antes (rowcount == 0 no INSERT OR IGNORE).

    `event`, `invoice_id` e `payload_raw` são gravados só como trilha de auditoria
    fiscal — nunca lidos pelo fluxo. Sem eles, uma entrega inesperada não deixa
    rastro do que a Notaas realmente mandou.
    """

    if isinstance(payload_raw, bytes):
        payload_raw = payload_raw.decode("utf-8")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO ntaas_deliveries (delivery_id, event, invoice_id, payload) "
            "VALUES (?, ?, ?, ?)",
            (delivery_id, event, invoice_id, payload_raw),
        )
        return cursor.rowcount == 0
