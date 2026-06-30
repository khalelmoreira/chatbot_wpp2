from src.types import ContextTomador, ConversationStatus, StatusResumo, HistoryResumo
from src.managers.conversations import ConversationManager, OnboardingManager

class ResumoBuilder:
    def __init__(self, ctx: ContextTomador, status: ConversationStatus):
        self.ctx = ctx
        self.status = status
        self.conv_manager = ConversationManager(ctx)
        self.on_manager = OnboardingManager(ctx)

    def resumo_status(self) -> StatusResumo:
        builders = {
            ConversationStatus.COLLECTING: self._get_draft,
            ConversationStatus.CONFIRMING: self._get_draft,
            ConversationStatus.QUEUED:     self._get_nfs,
            ConversationStatus.DONE:       self._get_nfs,
            ConversationStatus.ERROR:      self._get_nfs,
            ConversationStatus.CANCELLED:  self._get_nfs,
        }
        get_data = builders.get(self.status)
        print(f"GET_DATA RESUMO_STATUS: {get_data}\n")
        if get_data is None:
            return StatusResumo()
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
    
    def _get_history(self):
        return dict(self.on_manager.get_nf_history(limit=5))
    
    def resumo_history(self) -> HistoryResumo:
        history = self._get_history()
        
        return HistoryResumo(
            id=history.get("id"),
            status=history.get("status"),
            conversation_id=history.get("conversation_id"),
            tentativas=history.get("tentativas"),
            payload_enviado=history.get("payload_enviado"),
            requested_at=history.get("requested_at"),
            created_at=history.get("created_at"),
            invoice_id=history.get("invoice_id"),
            emitido_em=history.get("emitido_em"),
            issued_at=history.get("issued_at"),
            erro_code=history.get("erro_code"),
            erro_msg=history.get("erro_msg"),
            cancelled_at=history.get("cancelled_at"),
        )