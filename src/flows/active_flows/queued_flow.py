from src.managers.conversations.conv_manager import ConvManager
from src.managers.msg_manager import MsgManager
from src.services.sender import get_sender
from src.types import ContextTomador, Role


def queued_flow(ctx: ContextTomador, conversation: ConvManager):

    msg = "⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!"
    MsgManager(ctx).save_msg(Role.AI, msg)
    get_sender(ctx.user.channel).send_msg_text(ctx.user.phone, msg)
    return