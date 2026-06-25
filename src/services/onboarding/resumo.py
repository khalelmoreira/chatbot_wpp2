import sqlite3
from src.types import ContextTomador, ConversationStatus, StatusResumo
from src.managers.conversations import ConversationManager, OnboardingManager

class ResumoBuilder:
    def __init__(self, ctx: ContextTomador, status: ConversationStatus):
        self.ctx = ctx
        self.status = status
        self.conv_manager = ConversationManager(self.ctx)
        self.on_manager = OnboardingManager(self.ctx)

    def resumo_status(self) -> StatusResumo | None:
        builders = {
            ConversationStatus.COLLECTING: self._get_draft,
            ConversationStatus.CONFIRMING: self._get_draft,
            ConversationStatus.QUEUED:     self._get_nfs,
            ConversationStatus.DONE:       self._get_nfs,
            ConversationStatus.ERROR:      self._get_nfs,
            ConversationStatus.CANCELLED:  self._get_nfs,
        }
        get_data = builders.get(self.status)
        if get_data is None:
            return None
        return self._build_resumo(dict(get_data()))
    
    def _get_nfs(self):
        return self.on_manager.resumo_nfs()

    def _get_draft(self):
        return self.conv_manager.get_all()
    
    def _build_resumo(self, conv: dict) -> StatusResumo:
        return StatusResumo(
            nf_status=conv.get("status"),
            erro_msg=conv.get("erro_msg"),
            created_at=conv.get("created_at"),
            updated_at=conv.get("updated_at"),
            invoice_id=conv.get("invoice_id"),
            draft=conv.get("draft_json"),
            requested_at=conv.get("requested_at"),
            cancelled_at=conv.get("cancelled_at"),
            emitido_em=conv.get("emitido_em"),
        )