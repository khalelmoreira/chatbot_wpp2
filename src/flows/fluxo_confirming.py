from src.managers.conversation_manager import ConversationManager
from src.types.context_tomador import ContextTomador
from src.types.incoming_msg import IncomingMessage
from src.models.conversation_state import ConversationStatus
from src.services.msg_service import send_msg_text
from src.managers.tomador_manager import TomadorManager

def fluxo_confirming(ctx: ContextTomador, conversation: ConversationManager, msg: IncomingMessage) -> None:
    
    if msg.tipo != "button_reply":
        #send_msg_text(msg.phone, "Por favor, use os botões para confirmar ou corrigir o endereço.")
        print(f"Por favor, use os botões para confirmar ou corrigir o endereço.\n")
        return
    
    if msg.id_botao == "tomador_confirmado":
        tomador = TomadorManager()
        conversation.update_state(ctx.conversation_id, ConversationStatus.QUEUED)
        tomador.update_nf_from_draft(ctx, conversation)
        worker.get_job
        return

    if msg.id_botao == "tomador_corrigir":
        conversation.update_state(ctx.conversation_id, ConversationStatus.COLLECTING)
        send_msg_text(
            msg.text,
            "Por favor, digite os dados do tomador novamente para podermos continuar"
        )
        print("Por favor, digite os dados do tomador novamente para podermos continuar\n")
        return