from config import MAX_TENTATIVAS
from src.database.db import DB
from src.database.get_connection import get_connection
from src.types import NfseStatus, NfsJob
from src.utils.debug import print_table


class NfsWorkerManager:
    def __init__(self, job: NfsJob):
        self.db  = DB()
        self.job = job
        self.jid = job.id
        self.cid = job.conv_id

    @classmethod
    def reserva_job(cls) -> "NfsWorkerManager | None":
        job = cls._get_next_job()
        if not job:
            return None
        return cls(job)
    
    @staticmethod
    def _get_next_job() -> NfsJob | None:

        row = DB().fetchone_exe("""
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
                conv_id,
                nome,
                cnpj,
                descricao_servico,
                valor_total,
                aliquota_iss,
                tentativas
        """, (MAX_TENTATIVAS,))
        if row is None:
            return None
        return NfsJob.from_dict(dict(row))
    
    def marcar_emitido(self) -> None:

        with get_connection() as conn:
            conn.execute("BEGIN")

            conn.execute(f"""
                UPDATE nfs
                SET status = '{NfseStatus.ISSUED}',
                    processado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.jid,))
            print_table(table_name="nfs", columns=["status", "processado_em"], where="id = ?", params=(self.jid,))

            conn.execute("""
                UPDATE conversations
                SET status = 'DONE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.cid,))
            print_table(
                table_name="conversations",
                columns=["status", "updated_at"],
                where="id = ?",
                params=(self.cid,),
            )

            conn.execute("COMMIT")

    def marcar_erro(self, tentativas: int, erro: str) -> None:
        novo_status = 'ERROR' if tentativas >= MAX_TENTATIVAS else 'QUEUED'
        self.db.update(
            "nfs",
            data={"status": novo_status, "erro_msg": erro, "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.jid}
        )

    def save_invoice_id(self, invoice_id: str) -> None:
        self.db.update(
            "nfs",
            data={"invoice_id": invoice_id, "status": "EMITTING", "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.jid}
        )

    def resetar_jobs_travados(self) -> None:
        self.db.exe("""
            UPDATE nfs SET
                status     = 'QUEUED',
                updated_at = CURRENT_TIMESTAMP
            WHERE status = 'PROCESSING'
              AND processado_em < DATETIME('now', '-5 minutes')
        """, ())