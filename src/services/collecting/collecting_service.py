from src.services.validators.validador_tomador import ValidadorTomador
from src.types import ContextTomador, ConversationStatus, IntentTipo
from src.managers.conversations.conversation_manager import ConversationManager
from chatbot_wpp2.src.services.ai.ai_service import AIService, AIAssitant
from src.services.onboarding.resumo import ResumoBuilder
from src.services.shared.msg_service import WhatsAppService
from src.utils.unpack_json import unpack_dados_db
from src.utils.unflatten import unflatten
from src.utils.debug import print_table

class CollectingService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.conversation = conversation
        self.validador = ValidadorTomador()
        self.ai = AIService(self.ctx)
        self.assistant = AIAssitant(self.ctx)
        self.wpp = WhatsAppService()
    
    def _update_draft(self):
        draft_dict = unflatten(self.ctx.validacao.validos)
        self.conversation.update_draft(draft_dict)
    
    def _update_state(self):
        self.conversation.update_state(ConversationStatus.CONFIRMING)

    def _msg_confirm(self):
        # send_msg_botao(
        #     phone=self.ctx.user.phone,
        #     text=(
        #         f"*Dados do tomador:*\n\n"
        #         f"{self.ctx.dados_completos.tomador.nome}\n"
        #         f"{self.ctx.dados_completos.tomador.cnpj}\n"
        #         f"{self.ctx.dados_completos.servico.descricao}\n"
        #         f"{self.ctx.dados_completos.valores.total}\n"
        #         f"Esses dados estão corretos?"
        #     ),
        #     botoes=[
        #         BotaoResponse(id="tomador_confirmado", title="✅ Confirmar"),
        #         BotaoResponse(id="tomador_corrigir", title="✏️ Corrigir"),
        #     ],
        # )

        print(
            f"*Dados do tomador:*\n\n"
            f"{self.ctx.dados_completos.tomador.nome}\n"
            f"{self.ctx.dados_completos.tomador.cnpj}\n"
            f"{self.ctx.dados_completos.servico.descricao}\n"
            f"{self.ctx.dados_completos.valores.total}\n"
            f"Esses dados estão corretos?"
        )
        print_table(table_name="conversations", where=self.ctx.user.phone)

    def _incompleto(self):
        pendencias = (self.ctx.validacao.invalidos + self.ctx.validacao.faltantes)
        #self.wpp.send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)
        print(f"Parece que ficou faltando esses dados:")
        print(f"pendencias: {pendencias}\n")

class IntentService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.assistant = AIAssitant(ctx)
        self.conversation = conversation
        self.resumo = ResumoBuilder(self.ctx, self.ctx.conv_status)

    def criar_conv_se(self):

        if self.ctx.conversation_id is None:
            return True
        
        intencao = self._intent()

        handlers = {
            IntentTipo.EMITIR:   self._emitir,
            IntentTipo.CONSULTA: self._consulta,
            IntentTipo.NENHUM:   self._no_intent,
        }
        handler = handlers.get(intencao)
        if not handler:
            raise ValueError(f"Intenção de usuario não tratada: {intencao}")
        return handler()
    
    def handle_active(self, extraction: ExtractionService) -> bool:
        extraction.extract_e_merge()

    def _intent(self):
        intencao = self.assistant.classificar_intent()
        print(f"INTENCAO: {intencao}\n")
        return intencao

    def _no_intent(self):
        response = self.assistant.no_intent_response()
        #self.wpp.send_msg_text(self.ctx.user.phone, response)
        print(f"RESPONSE: {response}\n")
        return False

    def _emitir(self) -> bool:
        self.ctx.conversation_id = self.conversation.create_conversation()
        return True
    
    def _consulta(self) -> bool:
        resumo_data = self.resumo.resumo_status()
        response = self.assistant.status_response(resumo_data)
        _notf_user(response)
        return False
    

class ExtractionService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.ai = AIService(self.ctx)
        self.conversation = conversation

    def extract_e_merge(self):

        self.ai.extract_nfse_data(self.ctx)
        print(f"DADOS NOVOS: {self.ctx.dados_novos}\n")

        draft = self.conversation.get_draft()
        self.ctx.dados_db = unpack_dados_db(draft)
        print(f"DADOS DRAFT:{self.ctx.dados_db}\n")

        self.ctx.dados_completos = self.ctx.dados_db.merge(self.ctx.dados_novos)
        print(f"MERGE: {self.ctx.dados_completos}\n")


class ValidationService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.validador = ValidadorTomador()
        self.conversation = conversation

    def valido_e_completo(self):

        self.validador.validar(self.ctx)
        print(f"VALIDACAO: {self.ctx.validacao}\n")

        if self.ctx.validacao.validos:
            self._update_draft()

            if not self.ctx.validacao.is_complete:
                self._incompleto()
                return

            self._update_draft()
            self._update_state()
            self._msg_confirm()
            return
        
        print(f"SEM DADOS VALIDOS\nVALIDOS: {self.ctx.validacao.validos}\n")
        return