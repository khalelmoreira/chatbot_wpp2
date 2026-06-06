from typing import Optional
from config import MAX_TENTATIVAS
from src.database.db import executar_modif, fetchone

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