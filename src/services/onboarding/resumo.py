from src.managers.conversations import ConvManager, OnboardingManager
from src.types import ContextTomador, ConvStatus, HistoryResumo, MsgResumo, StatusResumo


class ResumoBuilder:
    def __init__(self, ctx: ContextTomador, status: ConvStatus):
        self.ctx = ctx
        self.status = status
        self.conv_manager = ConvManager(ctx)
        self.on_manager = OnboardingManager(ctx)

    def resumo_status(self) -> StatusResumo:
        builders = {
            ConvStatus.COLLECTING: self._get_draft,
            ConvStatus.CONFIRMING: self._get_draft,
            ConvStatus.QUEUED:     self._get_nfs,
            ConvStatus.DONE:       self._get_nfs,
            ConvStatus.ERROR:      self._get_nfs,
            ConvStatus.CANCELLED:  self._get_nfs,
        }
        get_data = builders.get(self.status)
        if get_data is None:
            return StatusResumo()
        row = get_data()
        if row is None:
            return StatusResumo()
        return StatusResumo.from_row(row)
    
    def _get_nfs(self):
        return self.on_manager.resumo_nfs()

    def _get_draft(self):
        return self.conv_manager.get_all()

    def resumo_nfs_history(self) -> list[HistoryResumo]:
        rows = self.on_manager.get_nf_history(limit=5)
        return [HistoryResumo.from_row(row) for row in rows]

    def resumo_msg_history(self) -> list[MsgResumo]:
        rows = self.on_manager.get_msg_history(limit=5)
        return [MsgResumo.from_row(row) for row in rows]