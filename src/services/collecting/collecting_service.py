from src.services.validators.validador_tomador import ValidadorTomador
from src.types import ContextTomador, ConversationStatus, IntentTipo, Role, BotaoResponse
from src.managers.conversations.conversation_manager import ConversationManager
from src.managers.messages.msg_manager import MsgManager
from chatbot_wpp2.src.services.ai.ai_service import AIService, AIAssitant
from src.services.onboarding.resumo import ResumoBuilder
from chatbot_wpp2.src.services.wpp.msg_service import WhatsAppService
from src.utils.unpack_json import unpack_dados_db
from src.utils.unflatten import unflatten
from src.utils.debug import print_table

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.assistant = AIAssitant(ctx)
        self.conversation = conversation
        self.resumo = ResumoBuilder(ctx, ctx.conv_status)
        self.msg = MsgManager(ctx)

    def criar_conv_se(self) -> bool:

        if self.ctx.conversation_id is None:
            intencao = self._intent()

            match intencao:
                case IntentTipo.EMITIR:
                    self.ctx.conversation_id = self.conversation.create_conversation()
                    return True
                
                case IntentTipo.CONSULTA:

                    resumo_data = self.resumo.resumo_status()
                    response = self.assistant.status_response(resumo_data)

                    self.msg.save_msg(role=Role.AI, content=response)
                    notf_user(response)
                    return False
                
                case IntentTipo.NENHUM:

                    response = self.assistant.no_intent_response()
                    self.msg.save_msg(role=Role.AI, content=response)

                    notf_user(response)
                    return False
                
                case _:
                    raise ValueError(f"Intenção de usuario não tratada: {intencao}")
    
        return True
    
    def _intent(self):
        intencao = self.assistant.classificar_intent()
        print(f"INTENCAO: {intencao}\n")
        return intencao

    def _no_intent(self):
        response = self.assistant.no_intent_response()
        #self.wpp.send_msg_text(self.ctx.user.phone, response)
        print(f"RESPONSE: {response}\n")
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
        
        print(f"SEM DADOS VALIDOS\nVALIDOS: {self.ctx.validacao.validos}\n")
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
        pendencias = (self.ctx.validacao.invalidos + self.ctx.validacao.faltantes)
        self.msg.save_msg(Role.AI, f"Parece que ficou faltando esses dados: {pendencias}")
        #self.wpp.send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)
        print(f"Parece que ficou faltando esses dados:")
        print(f"pendencias: {pendencias}\n")