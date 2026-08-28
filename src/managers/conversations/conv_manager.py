import json
from typing import Any

from src.database.db import DB
from src.types import ContextTomador, Conversation


class ConvManager:
    def __init__(self, ctx: ContextTomador):
        self.db = DB()
        self.ctx = ctx
        self.id = ctx.user.id
        self.phone = ctx.user.phone

    @property
    def cid(self) -> int | None:
        """Lido de ctx.conv_id a cada acesso, não capturado no __init__ — um
        ConvManager pode ser construído antes de uma conversa nova existir
        (ex.: IntentService cria a conversa e reusa a mesma instância para
        collecting_flow); um snapshot em __init__ ficaria travado em None."""
        return self.ctx.conv_id


    def get_all(self) -> Conversation | None:
        row = self.db.select(
            "conversations",
            where={"prestador_id": self.id},
            order_by="created_at DESC",
            limit=1
        )
        if row is None:
            return None
        return Conversation.from_dict(dict(row[0]))
    
    def get_status(self) -> str:
        row = self.db.select(
            "conversations",
            columns="status",
            where={"phone": self.phone}
        )
        return row[0]["status"]

    def get_ativa(self) -> Conversation | None:

        row = self.db.fetchone("""
            SELECT * FROM conversations
            WHERE prestador_id = ?
                AND status NOT IN ('DONE', 'ERROR', 'CANCELLED')
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.id,))
        if row is None:
            return None
        return Conversation.from_dict(dict(row))
        
    def create_conversation(self) -> int:
        row = self.db.insert(
            "conversations",
            data={
                "phone": self.phone,
                "prestador_id": self.id,
                "status": "COLLECTING",
                "draft_json": "{}",
            },
            returning="id"
        )
        return row
    
    def update_state(self, novo_status: str) -> None:
        self.db.update(
            "conversations",
            data={"status": novo_status, "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.cid}
        )

    def get_draft(self) -> dict[str, Any] | None:
        row = self.db.select_one(
            "conversations",
            columns="draft_json",
            where={"id": self.cid}
        )
        if row is None:
            return None
        return json.loads(row["draft_json"])

    def update_draft(self, draft: dict[str, Any]) -> None:
        self.db.update(
            "conversations",
            data={"draft_json": json.dumps(draft), "updated_at": "CURRENT_TIMESTAMP"},
            where={"id": self.cid}
        )