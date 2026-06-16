from src.managers.tomador_manager import TomadorManager
from chatbot_wpp2.src.services.validators.validador_tomador import ValidadorTomador
from src.types.context_tomador import ContextTomador
from src.managers.conversation_manager import ConversationManager
from chatbot_wpp2.src.services.shared.ai_service import has_intent, no_intent_response

class CollectingService:
    def __init__(self):
        self.tomador = TomadorManager()
        self.validador = ValidadorTomador()

    def processar(self, ctx: ContextTomador, conversation: ConversationManager):

       if not self._criar_conversa_se_necessario(ctx, conversation):
           return
       
       self._extrair_dados(ctx)
       self._carregar_draft(ctx, conversation)
       self._merge_dados(ctx)

       return self._validar_e_atualizar(ctx, conversation)
    
    def _criar_conversa_se(self, ctx, conversation):
        if ctx.conversation_id is None:
            intencao = has_intent(ctx)
            print(f"INTENCAO: {intencao}\n")

            if not intencao:
                response = no_intent_response(ctx)
                print(f"RESPONSE: {response}\n")
                #send_msg_text(ctx.user.phone, response)
                return False
            
        ctx.conversation_id = conversation.create_conversation(ctx)
        return True