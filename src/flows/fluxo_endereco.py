from src.managers.user_manager import UserManager
from src.types.incoming_msg import IncomingMessage
from src.types.estado_user import EstadoUser

def fluxo_endereco(
        msg: IncomingMessage,
        user_manager: UserManager,
):
    if msg.tipo != "button_reply":
        #send_msg_text(msg.phone, "Por favor, use os botões para confirmar ou corrigir o endereço.")
        return
    
    if msg.id_botao == "endereco_confirmado":
        user_manager.update_state(msg.phone, EstadoUser.CRIANDO_PROJETO_NOTAAS)
        return criar_project()
    
    if msg.id_botao == "endereco_corrigir":
        user_manager.update_state(msg.phone, EstadoUser.CADASTRO_ENDERECO_MANUAL)
        # send_msg_text(
        #     msg.phone,
        #     "Sem problema. Por favor, envie seu endereço completo no seguinte formato:\n\n"
        #     "Logradouro, Número, Bairro, Cidade, UF, CEP",
        #     )