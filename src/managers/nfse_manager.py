import sqlite3
from src.database.db import DB
from src.types import NfNotFoundError

class NfsManager:
    def __init__(self, data: dict):
        self.data            = data
        self.db              = DB()
        self.invoice_id      = data.get("invoiceId")
        self.nf              = self.get_nf()
        self.conversation_id = self.nf["conversation_id"]

    def get_nf(self):
        nf = self.db.fetchone(
            "SELECT id, conversation_id FROM nfs WHERE invoice_id = ?",
            (self.invoice_id,)
        )
        if not nf:
            raise NfNotFoundError(f"NF não encontrada para invoiceId={self.invoice_id}")

        return nf
    
    def get_phone(self) -> sqlite3.Row | None:
        row = self.db.fetchone("""
            SELECT p.phone FROM conversations c
            JOIN prestador p ON p.id = c.prestador_id
            WHERE c.id = ?
        """, (self.conversation_id,))

        if row:
            return row
        
    def reset_conv(self, novo_status: str) -> None:

        self.db.executar_modif("""
            UPDATE conversations SET
                status     = ?,
                draft_json = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, self.conversation_id))

    def update_nf_done(self):

        self.db.executar_modif("""
            UPDATE nfs SET
                status       = 'DONE',
                ch_nfse      = ?,
                numero_nfse  = ?,
                emitido_em   = ?,
                updated_at   = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            self.data.get("chNFSe"),
            self.data.get("numeroNfe"),
            self.data.get("emittedAt"),
            self.nf["id"],
        ))

    def update_nf_error(self):

        error_msg = self.data.get("errorMessage", "Erro desconhecido")

        self.db.executar_modif("""
            UPDATE nfs SET
                status           = 'ERROR',
                error_code       = ?,
                error_msg        = ?,
                updated_at       = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (self.data.get("errorCode"), error_msg, self.nf["id"]))

    def update_nf_cancelled(self):

        self.db.executar_modif("""
            UPDATE nfs SET
                status        = 'CANCELLED',
                cancelled_at  = ?,
                updated_at    = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (self.data.get("cancelledAt"), self.nf["id"]))

    def coalesce(self):

        pdf_url         = self.data.get("pdfUrl")
        xml_url         = self.data.get("xmlUrl")

        self.db.executar_modif(
            """
            UPDATE nfs SET
                pdf_url    = COALESCE(?, pdf_url),
                xml_url    = COALESCE(?, xml_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (pdf_url, xml_url, self.nf["id"])
        )