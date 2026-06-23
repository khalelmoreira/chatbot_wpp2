import sqlite3
from src.types import StatusInvoice
from src.database.db import DB
from src.types import NfseStatus

class NfsPollingManager:
    def __init__(self, job: int):
        self.db     = DB()
        self.job    = job
        self.job_id = job["id"]

    @classmethod
    def get_jobs(cls) -> "list[NfsPollingManager]":
        jobs = cls._get_processing_invoice()
        return [cls(job) for job in jobs]

    @staticmethod
    def _get_processing_invoice() -> list[sqlite3.Row]:
        
        db = DB()
        result =  db.fetchall("""
            SELECT
                id,
                conversation_id,
                invoice_id,
                prestador_id
            FROM nfs
            WHERE status = ?
                AND invoice_id IS NOT NULL
            ORDER BY processado_em ASC
        """, (NfseStatus.PROCESSING,))

        return result or []

    def marcar_issued(self, result: StatusInvoice) -> bool:
        """Retorna True se a transição foi aplicada, False se já não estava em processing."""

        row = self.db.fetchone_modif("""
            UPDATE nfs SET
                status = ?,
                ch_nfse = ?,
                n_nfse = ?,
                issued_at = ?
            WHERE id = ?
            AND status = ?
                RETURNING id
        """, (NfseStatus.ISSUED, result.ch_nfse, result.n_nfse, result.issued_at, self.job_id, NfseStatus.PROCESSING))

        return row is not None
    
    def marcar_erro(self, error_msg: str) -> bool:

        row = self.db.fetchone_modif("""
            UPDATE nfs SET
                status = ?,
                erro_msg = ?
            WHERE id = ?
            AND status = ?
                RETURNING id
        """, (NfseStatus.ERROR, error_msg, self.job_id, NfseStatus.PROCESSING))

        return row is not None
    
    def marcar_cancelled(self) -> bool:

        row = self.db.fetchone_modif("""
            UPDATE nfs SET
                status = ?,
            WHERE id = ?
            AND status = ?
                RETURNING id
        """, (NfseStatus.CANCELLED, self.job_id, NfseStatus.PROCESSING))

        return row is not None