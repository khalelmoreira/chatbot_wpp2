from src.types.incoming_msg import IncomingMessage
import sqlite3
from src.database.db import fetchone, executar_modif
from src.services.shared.msg_service import send_msg_text

class NfNotFoundError(Exception):
    pass

class NfseService:
    def __init__(self, data: dict):
        self.data            = data
        self.invoice_id      = data.get("invoiceId")
        self.nf              = self._get_nf()
        self.conversation_id = self.nf["conversation_id"]

    def _get_nf(self):
        nf = fetchone(
            "SELECT id, conversation_id FROM nfs WHERE invoice_id = ?",
            (self.invoice_id,)
        )
        if not nf:
            raise NfNotFoundError(f"NF não encontrada para invoiceId={self.invoice_id}")

        return nf
    
    def _get_phone(self) -> sqlite3.Row | None:
        row = fetchone("""
            SELECT p.phone FROM conversations c
            JOIN prestador p ON p.id = c.prestador_id
            WHERE c.id = ?
        """, (self.conversation_id,))

        if row:
            return row
    
    def _notf_prestador(self, msg: str) -> None:
        row = self._get_phone()
        send_msg_text(row["phone"], msg)

    def _finalizar_conv(self, novo_status: str, msg: str) -> None:

        executar_modif("""
            UPDATE conversations SET
                status     = ?,
                draft_json = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, self.conversation_id))

        row = self._get_phone()
        send_msg_text(row["phone"], msg)

    def issued(self):
        
        executar_modif("""
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

        # self._finalizar_conv(
        #     self.conversation_id,
        #     novo_status="COLLECTING",
        #     msg=(
        #         f"✅ Nota emitida com sucesso!\n"
        #         f"Número: {self.data.get('numeroNfe')}\n"
        #         f"Chave: {self.data.get('chNFSe')}"
        #     )
        # )
        print(
            self.conversation_id,
            f"✅ Nota emitida com sucesso!\n"
            f"Número: {self.data.get('numeroNfe')}\n"
            f"Chave: {self.data.get('chNFSe')}\n"
        )

        return {"success": True}

    def error(self):
        
        error_msg = self.data.get("errorMessage", "Erro desconhecido")
        errors    = self.data.get("errors", [])

        detalhes = "\n".join(
            f" • [{e.get('Codigo')}] {e.get('Descricao')}"
            for e in errors
        )

        executar_modif("""
            UPDATE nfs SET
                status           = 'ERROR',
                error_code       = ?,
                error_msg        = ?,
                updated_at       = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (self.data.get("errorCode"), error_msg, self.nf["id"]))

        # self._finalizar_conv(
        #     self.conversation_id,
        #     novo_status="COLLECTING",
        #     msg=(
        #         f"❌ Falha na emissão da nota.\n"
        #         f"Motivo: {error_msg}"
        #         + (f"\n{detalhes}" if detalhes else "")
        #     )
        # )
        print(
            self.conversation_id,
            f"❌ Falha na emissão da nota.\n"
            f"Motivo: {error_msg}"
            + (f"\n{detalhes}\n" if detalhes else "\n")
        )

        return {"success": True}

    def cancelled(self):
        
        executar_modif("""
            UPDATE nfs SET
                status        = 'CANCELLED',
                cancelled_at  = ?,
                updated_at    = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (self.data.get("cancelledAt"), self.nf["id"]))

        # self._finalizar_conv(
        #     self.conversation_id,
        #     novo_status="COLLECTING",
        #     msg="🚫 Nota fiscal cancelada."
        #     )
        
        print(
            self.conversation_id,
            "🚫 Nota fiscal cancelada.\n"
        )

        return {"success": True}

    def docs_ready(self):

        document_status = self.data.get("documentStatus")   # "partial" | "complete"
        pdf_url         = self.data.get("pdfUrl")
        xml_url         = self.data.get("xmlUrl")
        
        # COALESCE: não sobrescreve URL já salva com null
        executar_modif(
            """
            UPDATE nfs SET
                pdf_url    = COALESCE(?, pdf_url),
                xml_url    = COALESCE(?, xml_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (pdf_url, xml_url, self.nf["id"])
        )

        if document_status == "complete" and pdf_url:
            # self._notf_prestador(
            #     self.conversation_id,
            #     f"📄 PDF da nota disponível:\n{pdf_url}"
            # )
            print(
                self.conversation_id,
                f"📄 PDF da nota disponível:\n{pdf_url}\n"
            )

        return {"success": True}
