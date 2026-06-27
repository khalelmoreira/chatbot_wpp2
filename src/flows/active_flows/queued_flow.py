from src.types import ContextTomador, Role
from src.managers.conversations.conversation_manager import ConversationManager
from chatbot_wpp2.src.services.wpp.msg_service import WhatsAppService
from src.managers.messages.msg_manager import MsgManager

def queued_flow(ctx: ContextTomador, conversation: ConversationManager):

    wpp = WhatsAppService()
    MsgManager(ctx).save_msg(Role.AI, "⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!")
    # wpp.send_msg_text(
    #     ctx.user.phone,
    #     "⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!"
    # )
    print("⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!\n")
    return