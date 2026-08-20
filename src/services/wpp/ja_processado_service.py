from src.database.get_connection import get_connection


def ja_processado(msg_id: str) -> bool:
    """Mesmo padrão de `src.services.ntaas.ja_process.ja_process`, aplicado ao
    id de mensagem do WhatsApp: a Meta pode reentregar o mesmo webhook (timeout
    de resposta, retry de rede) — sem isso, uma mensagem duplicada dispararia
    extração/emissão duas vezes."""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO wpp_mensagens_processadas (msg_id) VALUES (?)",
            (msg_id,)
        )
        return cursor.rowcount == 0
