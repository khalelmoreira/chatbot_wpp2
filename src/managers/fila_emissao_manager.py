from typing import Optional
from config import MAX_TENTATIVAS
import sqlite3
from src.database.db import executar_modif, fetchone, fetchone_modif
from src.database.get_connection import get_connection
from src.models.conversation_state import NfseStatus

class FilaManager:

    def get_reserva_job(self) -> Optional[dict]:

        return fetchone("""
                        
        UPDATE fila_emissao
        SET status = 'processando'
        WHERE id = (
            SELECT id FROM fila_emissao
            WHERE status = 'pendente'
                AND tentativas < ?
            ORDER BY id ASC
            LIMIT 1
        )
        RETURNING id, payload, tentativas
        """, (MAX_TENTATIVAS,)
        )

    def marcar_emitido(self, job_id: int) -> None:

        executar_modif("""
                    
        UPDATE fila_emissao
        SET status = 'emitido',
            processado_em = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (job_id,)
        )

    def marcar_erro(self, job_id: int, erro: Exception) -> None:

        executar_modif("""
                    
        UPDATE fila_emissao
        SET status = 'pendente',
            erro = ?,
            tentativas = tentativas + 1
        WHERE id = ?
        """, (str(erro), job_id)
        )

class NfsWorkerManager:

    def get_reserva_job(self) -> Optional[sqlite3.Row]:

        return fetchone_modif(f"""
            UPDATE nfs
            SET status = '{NfseStatus.PROCESSING}',
                processado_em = CURRENT_TIMESTAMP,
                tentativas = tentativas + 1
            WHERE id = (
            SELECT id FROM nfs
            WHERE status = '{NfseStatus.QUEUED}'
                AND tentativas < ?
            ORDER BY requested_at ASC
            LIMIT 1
            )
            RETURNING id, conversation_id, payload_enviado, tentativas
        """, (MAX_TENTATIVAS,))
    
    def marcar_emitido(self, job_id: int, conversation_id: int) -> None:

        with get_connection() as conn:
            conn.execute("BEGIN")

            conn.execute(f"""
                UPDATE nfs
                SET status = '{NfseStatus.ISSUED}',
                    processado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (job_id,))

            conn.execute("""
                UPDATE conversations
                SET status = 'DONE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (conversation_id,))

            conn.execute("COMMIT")

    def marcar_erro(self, job_id: int, erro: Exception) -> None:

        executar_modif(f"""
            UPDATE nfs
            SET status = '{NfseStatus.QUEUED}',
                erro_msg = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (str(erro), job_id))