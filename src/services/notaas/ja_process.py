from src.database.get_connection import get_connection

def ja_process(delivery_id: str) -> bool:
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO ntaas_deliveries (delivery_id) VALUES (?)",
            (delivery_id,)
        )
        return cursor.rowcount == 0