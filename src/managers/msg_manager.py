from src.database.db import executar_modif, fetchall

def get_msg_history(self, conversation_id: int) -> list[dict]:

        rows = fetchall("""
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        return [{"role": row["role"], "content": row["content"]} for row in rows]

def add_message(self, conversation_id: int, role: str, content: str) -> None:

    executar_modif("""
        INSERT INTO messages (conversation_id, role, content)
        VALUE (?, ?, ?)
    """, (conversation_id, role, content))