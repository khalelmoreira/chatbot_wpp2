import sqlite3
from typing import Any
import xml
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
            SELECT p.phone FROM conversations c
            JOIN prestador p ON p.id = c.prestador_id
            WHERE c.id = ?
        """, (self.cid,))
        if row is None:
            return None
        return dict(row)
        
    def reset_conv(self, novo_status: str) -> None:
        self.db.update(
            "conversations",
            data={"status": novo_status, "draft_json": "{}", "updated_at": "CURRENT_TIMESTAMP"},
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
                "updated_at": "CURRENT_TIMESTAMP"
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
                "updated_at": "CURRENT_TIMESTAMP"
            },
            where={"id": self.nfi}
        )

    def update_nf_cancelled(self) -> None:
        self.db.update(
            "nfs",
            data={
                "status": "CANCELLED",
                "cancelled_at": self.data.get("cancelledAt"),
                "updated_at": "CURRENT_TIMESTAMP"
            },
            where={"id": self.nf["id"]}
        )

    def coalesce(self) -> None:

        pdf_url = self.data.get("pdfUrl")
        xml_url = self.data.get("xmlUrl")

        self.db.update(
            "nfs",
            data={
                "pdf_url": f"COALESCE({pdf_url}, pdf_url)",
                "xml_url": f"COALESCE({xml_url}, xml_url)",
                "updated_at": "CURRENT_TIMESTAMP"
            },
            where={"id": self.nfi}
        )