import logging

from src.managers.nfs.nf_manager import NfsManager
from src.services.wpp.msg_service import WhatsAppService

logger = logging.getLogger(__name__)

class NfseService:
    def __init__(self, data: dict):
        self.data    = data
        self.manager = NfsManager(data)
        self.wpp     = WhatsAppService()
    
    def _notf_prestador(self, msg: str) -> None:
        row = self.manager.get_phone()
        if row is None:
            raise LookupError("phone/prestador_id não encontrado para user")
        #self.wpp.send_msg_text(row["phone"], msg)
        print(msg)


    def issued(self):

        logger.info("nf issued: conv_id/job processado")

        self.manager.update_nf_done()
        self.manager.reset_conv(novo_status="COLLECTING")

        self._notf_prestador(
            msg=(
                f"✅ Nota emitida com sucesso!\n"
                f"Número: {self.data.get('numeroNfe')}\n"
                f"Chave: {self.data.get('chNFSe')}"
            )
        )

        return {"success": True}

    def error(self):

        logger.info("nf error: webhook de erro recebido")

        error_msg = self.data.get("errorMessage", "Erro desconhecido")
        errors    = self.data.get("errors", [])

        detalhes = "\n".join(
            f" • [{e.get('Codigo')}] {e.get('Descricao')}"
            for e in errors
        )

        self.manager.update_nf_error()
        self.manager.reset_conv(novo_status="COLLECTING")

        self._notf_prestador(
            msg=(
                f"❌ Falha na emissão da nota.\n"
                f"Motivo: {error_msg}"
                + (f"\n{detalhes}" if detalhes else "")
            )
        )

        return {"success": True}

    def cancelled(self):

        logger.info("nf cancelled: webhook de cancelamento recebido")
        
        self.manager.update_nf_cancelled()
        self.manager.reset_conv(novo_status="COLLECTING") 
        self._notf_prestador(msg="🚫 Nota fiscal cancelada.")

        return {"success": True}

    def docs_ready(self):

        logger.info("nf docs ready: webhook recebido")

        document_status = self.data.get("documentStatus")   # "partial" | "complete"
        pdf_url         = self.data.get("pdfUrl")
        
        # COALESCE: não sobrescreve URL já salva com null
        self.manager.coalesce()

        if document_status == "complete" and pdf_url:
            self._notf_prestador(f"📄 PDF da nota disponível:\n{pdf_url}")

        return {"success": True}
