from src.managers.conversation_db import ConversationManager
from src.types.conversation_type import AIClient
from src.utils.conversation_helpers import is_cancel, is_confirm, campos_faltando, merge_draft


# ─── StateMachine ────────────────────────────────────────────────────────────

class StateMachine:
    def __init__(self, manager: ConversationManager, ai: AIClient, emission_queue):
        
        #MANAGER = TODAS AS FUNÇÕES DE ConversationManager

        self.manager = manager
        self.ai = ai
        self.emission_queue = emission_queue          # fila já existente

    def process(self, phone: str, message: str) -> str:

        conversation = self.manager.get_active_conversation(phone)

        # ── IDLE ──────────────────────────────────────────────────────────────

        if not conversation:
            return self._handler_idle(phone, message)
        
        conversation_id = conversation["id"]
        status = conversation["status"]

        # ── CANCELAMENTO — verificado antes de qualquer estado ────────────────

        if is_cancel(message):
            self.manager.add_message(conversation_id, "user", message)
            self.manager.update_state(conversation_id, "CANCELLED")

            return "Operação cancelada. Quando quiser emitir nova nota, é só me chamar."
        
        # ── Persiste mensagem do usuário ──────────────────────────────────────

        self.manager.add_message(conversation_id, "user", message)

        # ── Despacha para o handler do estado atual ───────────────────────────

        if status == "COLLECTING":
            return self._handle_collecting(conversation_id, message)
        
        if status == "CONFIRMING":
            return self._handle_confirming(conversation_id, message)
        
        if status == "EMITTING":
            return "Sua nota ainda esta sendo processada, aguarde um instante."
        
        return "Ocorreu um erro inesperado. Por favor, tente novamente."
        
    # ── Handlers por estado ───────────────────────────────────────────────────

    def _handler_idle(self, phone: str, message: str) -> str:

        """
        Em IDLE, a IA decide se há intenção de emitir nota.
        Se sim, cria conversa e já tenta extrair dados da primeira mensagem.
        """

        ai_response = self.ai.process(
            history=[{"role": "user", "content": message}],
            draft={},
            state="IDLE"
        )

        # IA não detectou intenção de emissão

        if not ai_response.extraido:
            return ai_response.message
        
        # Detectou intenção — abre conversa

        conversation_id = self.manager.create_conversation(phone)
        self.manager.add_message(conversation_id, "user", message)
        self.manager.add_message(conversation_id, "assistant", ai_response)
        self.manager.update_draft(conversation_id, ai_response.extraido)

        # Já atualiza draft com o que veio na primeira mensagem

        if ai_response.extraido:
            self.manager.update_draft(conversation_id, ai_response.extraido)

        # Verifica se a primeira mensagem já tinha tudo

        faltando = campos_faltando(ai_response.extraido)
        if not faltando:
            self.manager.update_state(conversation_id, "CONFIRMING")

        return ai_response.message
    
    def _handle_collecting(self, conversation_id: int, message: str) -> str:

        draft = self.manager.get_draft(conversation_id)
        history = self.manager.get_history(conversation_id)

        ai_response = self.ai.process(
            history=history,
            draft=draft,
            state="COLLECTING"
        )

        # Merge — nunca substitui dados válidos por None

        novo_draft = merge_draft(draft, ai_response.extraido)
        self.manager.update_draft(conversation_id, novo_draft)
        self.manager.add_message(conversation_id, "assistant", ai_response.message)

        # Transição para CONFIRMING se todos os campos estão presentes

        if not campos_faltando(novo_draft):
            self.manager.update_state(conversation_id, "CONFIRMING")

        return ai_response.message
    
    def _handle_confirming(self, conversation_id: int, message: str) -> str:
        if is_confirm(message):
            return self._trigger_emission(conversation_id)
        
        # Usuário quer corrigir — volta para COLLECTING

        self.manager.update_state(conversation_id, "COLLECTING")
        return self._handle_collecting(conversation_id, message)
    
    def _trigger_emission(self, conversation_id: int) -> str:
        self.manager.update_state(conversation_id, "EMITTING")
        draft = self.manager.get_draft(conversation_id)

        # Enfileira usando sua fila já existente

        self.emission_queue(
            conversation_id=conversation_id,
            dados=draft
        )

        return "Perfeito! Sua nota esta sendo emitida. Assim que concluir, te aviso aqui."