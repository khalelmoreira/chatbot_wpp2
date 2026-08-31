from typing import Any

from src.database.db import DB
from src.types import NfNotFoundError


class NfsManager:
    def __init__(self, data: dict):
        self.data = data
        self.db   = DB()
        self.ivid = data.get("invoiceId")
        self.nf   = self.get_nf()
        self.cid  = self.nf["conv_id"]
        self.nfi  = self.nf["id"]

    def get_nf(self) -> dict[str, Any]:
        nf = self.db.select(
            "nfs",
            columns="id, conv_id",
            where={"invoice_id": self.ivid}
        )
        if not nf:
            raise NfNotFoundError(f"NF não encontrada para invoiceId={self.ivid}")
        return dict(nf[0])
    
    def get_phone(self) -> dict[str, Any] | None:

        row = self.db.fetchone("""
            SELECT p.id AS prestador_id, p.phone, p.channel FROM conversations c
            JOIN prestador p ON p.id = c.prestador_id
            WHERE c.id = ?
        """, (self.cid,))
        if row is None:
            return None
        return dict(row)

    def save_ai_msg(self, prestador_id: int, phone: str, content: str) -> None:
        """Persiste no histórico uma notificação enviada ao prestador pelo fluxo de
        webhook (emissão/erro/cancelamento/PDF) — que roda sem ContextTomador e
        portanto sem MsgManager."""
        self.db.insert(
            "messages",
            data={"prestador_id": prestador_id, "phone": phone, "role": "AI", "content": content},
        )
        
    def reset_conv(self, novo_status: str) -> None:
        self.db.update(
            "conversations",
            data={"status": novo_status, "draft_json": "{}"},
            where={"id": self.cid}
        )

    def update_nf_done(self) -> None:
        self.db.update(
            "nfs",
            data={
                "status": "DONE",
                "ch_nfse": self.data.get("chNFSe"),
                "n_nfse": self.data.get("numeroNfe"),
                "emitido_em": self.data.get("emittedAt"),
            },
            where={"id": self.nfi}
        )

    def update_nf_error(self) -> None:
        self.db.update(
            "nfs",
            data={
                "status": "ERROR",
                "erro_code": self.data.get("errorCode"),
                "erro_msg": self.data.get("errorMessage", "Erro desconhecido"),
            },
            where={"id": self.nfi}
        )

    def update_nf_cancelled(self) -> None:
        self.db.update(
            "nfs",
            data={
                "status": "CANCELLED",
                "cancelled_at": self.data.get("cancelledAt"),
            },
            where={"id": self.nf["id"]}
        )

    def coalesce(self) -> None:

        pdf_url = self.data.get("pdfUrl")
        xml_url = self.data.get("xmlUrl")

        self.db.exe("""
            UPDATE nfs SET
                pdf_url    = COALESCE(?, pdf_url),
                xml_url    = COALESCE(?, xml_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pdf_url, xml_url, self.nfi))