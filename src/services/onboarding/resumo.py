import sqlite3
from src.types import ContextTomador, ConversationStatus, StatusResumo, HistoryResumo, MsgResumo
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
    
    def resumo_nfs_history(self) -> list[HistoryResumo]:
        rows = self.on_manager.get_nf_history(limit=5)
        return [self._row_to_resumo(row) for row in rows]

    def resumo_msg_history(self) -> list[MsgResumo]:
        rows = self.on_manager.get_msg_history(limit=5)
        return [MsgResumo(role=row["role"], content=row["content"]) for row in rows]

    def _row_to_resumo(self, row: sqlite3.Row) -> HistoryResumo:
        return HistoryResumo(
            id=row["id"],
            status=row["status"],
            conversation_id=row["conversation_id"],
            tentativas=row["tentativas"],
            nome=row["nome"],
            cnpj=row["cnpj"],
            descricao_servico=row["descricao_servico"],
            valor_total=row["valor_total"],
            requested_at=row["requested_at"],
            created_at=row["created_at"],
            invoice_id=row["invoice_id"],
            emitido_em=row["emitido_em"],
            issued_at=row["issued_at"],
            erro_code=row["erro_code"],
            erro_msg=row["erro_msg"],
            cancelled_at=row["cancelled_at"],
        )