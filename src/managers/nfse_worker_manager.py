from typing import Optional
from config import MAX_TENTATIVAS
import sqlite3
from src.database.db import executar_modif, fetchone, fetchone_modif
from src.database.get_connection import get_connection
from src.models.conversation_state import NfseStatus
from src.utils.debug import print_table

class NfsWorkerManager:

    def get_reserva_job(self) -> Optional[sqlite3.Row]:

        return fetchone_modif("""
            UPDATE nfs
            SET status = 'PROCESSING',
                processado_em = CURRENT_TIMESTAMP,
                tentativas = tentativas + 1
            WHERE id = (
            SELECT id FROM nfs
            WHERE status = 'QUEUED'
                AND tentativas < ?
            ORDER BY requested_at ASC
            LIMIT 1
            )
            RETURNING id, conversation_id, payload_enviado, tentativas
        """, (MAX_TENTATIVAS,))
    
    def marcar_emitido(self, job_id: int, conversation_id: int) -> None:

        print(f"\n\n----------------MARCAR EMITIDO----------------\n\n")

        with get_connection() as conn:
            conn.execute("BEGIN")

            conn.execute(f"""
                UPDATE nfs
                SET status = '{NfseStatus.ISSUED}',
                    processado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (job_id,))
            print_table(table_name="nfs", columns=["status", "processado_em"], where="id = ?", params=(job_id,))

            conn.execute("""
                UPDATE conversations
                SET status = 'DONE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (conversation_id,))
            print_table(table_name="conversations", columns=["status", "updated_at"], where="id = ?", params=(conversation_id,))

            conn.execute("COMMIT")

    def marcar_erro(self, job_id: int, tentativas: int, erro: str) -> None:
        novo_status = 'ERROR' if tentativas >= MAX_TENTATIVAS else 'QUEUED'
        executar_modif(f"""
            UPDATE nfs SET
                status     = ?,
                erro_msg   = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, erro, job_id))

    def save_invoice_id(self, job_id: int, invoice_id: str) -> None:
        executar_modif("""
            UPDATE nfs SET
                invoice_id = ?,
                status     = 'EMITTING',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (invoice_id, job_id,))

    def resetar_jobs_travados(self):
        executar_modif("""
            UPDATE nfs SET
                status     = 'QUEUED',
                updated_at = CURRENT_TIMESTAMP
            WHERE status = 'PROCESSING'
              AND processado_em < DATETIME('now', '-5 minutes')
        """, ())