from src.services.validators.validador_tomador import ValidadorTomador
from src.types import ContextTomador, ConversationStatus, Role, BotaoResponse, DadosTomador
from chatbot_wpp2.src.managers.conversations.conv_manager import ConvManager
from chatbot_wpp2.src.managers.msg_manager import MsgManager
from src.services.ai.ai_service import AIService
from src.services.wpp.msg_service import WhatsAppService
from src.utils.unflatten import unflatten
from src.utils.debug import print_table

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")
    
class ExtractionService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.ai = AIService()
        self.conversation = conversation

    def extract_e_merge(self):

        self.ai.extract_nfse_data()
        print(f"DADOS NOVOS: {self.ctx.dados_novos}\n")

        draft = self.conversation.get_draft()
        self.ctx.dados_db = DadosTomador.from_dict(draft)
        print(f"DADOS DRAFT:{self.ctx.dados_db}\n")

        self.ctx.dados_completos = self.ctx.dados_db.merge(self.ctx.dados_novos)
        print(f"MERGE: {self.ctx.dados_completos}\n")


class ValidationService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.ai = AIService(ctx)
        self.validador = ValidadorTomador()
        self.msg = MsgManager(ctx)
        self.wpp = WhatsAppService()

    def valido_e_completo(self):

        self.validador.validar(self.ctx)

        if self.ctx.validacao.validos:
            self._update_draft()

            if not self.ctx.validacao.is_complete:
                self._incompleto()
                return
            
            self._update_draft()
            self._update_state()
            self._msg_confirm()
            return
        
        if self.ctx.validacao.invalidos:
            self._invalidos()
            return
        
        self._no_data()
        return
    
    def _update_draft(self):
        draft_dict = unflatten(self.ctx.validacao.validos)
        self.conversation.update_draft(draft_dict)
        print(f"VALIDACAO: {self.ctx.validacao}\n")
    
    def _update_state(self):
        self.conversation.update_state(ConversationStatus.CONFIRMING)

    def _msg_confirm(self):

        confirmar = BotaoResponse(id="tomador_confirmado", title="✅ Confirmar")
        corrigir = BotaoResponse(id="tomador_corrigir", title="✏️ Corrigir")

        msg_button = self.wpp.format_msg_botao(
            text=(f"*Dados do tomador:*\n\n"
            f"{self.ctx.dados_completos.tomador.nome}\n"
            f"{self.ctx.dados_completos.tomador.cnpj}\n"
            f"{self.ctx.dados_completos.servico.descricao}\n"
            f"{self.ctx.dados_completos.valores.total}\n"
            f"Esses dados estão corretos?"
            ),
            botoes=[confirmar, corrigir],
        )
        self.msg.save_msg(Role.AI, msg_button)

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
        #     botoes=[confirmar, corrigir],
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
        response = self.ai.incomplete_response()
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _invalidos(self):
        response = self.ai.invalidos_response()
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _no_data(self):
        response = self.ai.no_data_response()
        self.msg.save_msg(Role.AI, response)
        notf_user(response)