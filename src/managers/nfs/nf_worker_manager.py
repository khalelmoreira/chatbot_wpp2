import sqlite3
from typing import Optional
from src.types import NfseStatus
from config import MAX_TENTATIVAS
from src.database.db import DB
from src.database.get_connection import get_connection
from src.utils.debug import print_table

class NfsWorkerManager:
    def __init__(self, job: int):
        self.db              = DB()
        self.job             = job
        self.job_id          = job["id"]
        self.conversation_id = job["conversation_id"]

    @classmethod
    def reserva_job(cls) -> "NfsWorkerManager | None":
        job = cls._get_next_job()
        
        if not job:
            return None
        return cls(job)
    
    @staticmethod
    def _get_next_job() -> Optional[sqlite3.Row]:

        db = DB()
        return db.fetchone_modif("""
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
            RETURNING 
                id,
                conversation_id,
                nome,
                cnpj,
                descricao_servico,
                valor_total,
                aliquota_iss,
                tentativas
        """, (MAX_TENTATIVAS,))
    
    def marcar_emitido(self) -> None:

        with get_connection() as conn:
            conn.execute("BEGIN")

            conn.execute(f"""
                UPDATE nfs
                SET status = '{NfseStatus.ISSUED}',
                    processado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.job_id,))
            print_table(table_name="nfs", columns=["status", "processado_em"], where="id = ?", params=(self.job_id,))

            conn.execute("""
                UPDATE conversations
                SET status = 'DONE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.conversation_id,))
            print_table(table_name="conversations", columns=["status", "updated_at"], where="id = ?", params=(self.conversation_id,))

            conn.execute("COMMIT")

    def marcar_erro(self, tentativas: int, erro: str) -> None:
        novo_status = 'ERROR' if tentativas >= MAX_TENTATIVAS else 'QUEUED'
        self.db.executar_modif(f"""
            UPDATE nfs SET
                status     = ?,
                erro_msg   = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, erro, self.job_id))

    def save_invoice_id(self, invoice_id: str) -> None:
        print(f"UPDATE nfs SET invoice_id\n")
        self.db.executar_modif("""
            UPDATE nfs SET
                invoice_id = ?,
                status     = 'EMITTING',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (invoice_id, self.job_id,))

    def resetar_jobs_travados(self):
        self.db.executar_modif("""
            UPDATE nfs SET
                status     = 'QUEUED',
                updated_at = CURRENT_TIMESTAMP
            WHERE status = 'PROCESSING'
              AND processado_em < DATETIME('now', '-5 minutes')
        """, ())