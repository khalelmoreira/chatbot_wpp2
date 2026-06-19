from src.services.validators.validador_tomador import ValidadorTomador
from src.types import ContextTomador
from src.managers.conversation_manager import ConversationManager
from src.types.conversation_state import ConversationStatus
from src.services.shared.ai_service import AIService
from src.services.shared.msg_service import WhatsAppService
from src.utils.unpack_json import unpack_dados_db
from src.utils.unflatten import unflatten
from src.utils.debug import print_table

class CollectingService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.conversation = conversation
        self.validador = ValidadorTomador()
        self.ai = AIService()
        self.wpp = WhatsAppService()
    
    def criar_conv_se(self) -> bool:

        if self.ctx.conversation_id is None:
            intencao = self._intent()

            if not intencao:
                print(f"NO INTENCAO\n")
                self._no_intent()
                return False
            self._create_conversation_id()
            return True

        else:
            intencao = self._intent()
            
            if not intencao:
                self._no_intent()
                return False
            return True
        
    def extract_e_merge(self):

        self.ai.extract_nfse_data(self.ctx)
        print(f"DADOS NOVOS: {self.ctx.dados_novos}\n")

        draft = self.conversation.get_draft()
        self.ctx.dados_db = unpack_dados_db(draft)
        print(f"DADOS DRAFT:{self.ctx.dados_db}\n")

        self.ctx.dados_completos = self.ctx.dados_db.merge(self.ctx.dados_novos)
        print(f"MERGE: {self.ctx.dados_completos}\n")

        self.validador.validar(self.ctx)
        print(f"VALIDACAO: {self.ctx.validacao}\n")
        
    def valido_e_completo(self):

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
    
    def _intent(self):
        intencao = self.ai.has_intent(self.ctx)
        print(f"INTENCAO: {intencao}\n")
        return intencao

    def _no_intent(self):
        response = self.ai.not_intent_response(self.ctx)
        #self.wpp.send_msg_text(self.ctx.user.phone, response)
        print(f"RESPONSE: {response}\n")

    def _create_conversation_id(self):
        self.ctx.conversation_id = self.conversation.create_conversation()
    
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