from src.types import ContextTomador
from src.managers.conversations.conversation_manager import ConversationManager
from src.services.shared.msg_service import WhatsAppService

def fluxo_queued(ctx: ContextTomador, conversation: ConversationManager):

    wpp = WhatsAppService()
    # wpp.send_msg_text(
    #     ctx.user.phone,
    #     "⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!"
    # )
    print("⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!\n")
    return