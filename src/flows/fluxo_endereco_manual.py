from src.managers.user_manager import UserManager
from src.types.incoming_msg import IncomingMessage
from src.types.estado_user import EstadoUser
from src.managers.prestador_manager import PrestadorManager

def fluxo_endereco_manual(
        ctx_meta: IncomingMessage,
        user_manager: UserManager
):
    
    prestador_manager = PrestadorManager()
    endereco = extract_endereco(ctx_meta.text)

    if endereco is None:
        # send_msg_text(
        #     ctx_meta.phone,
        #     "Não consegui identificar o endereço. Tente no formato:\n\n"
        #     "Logradouro, Número, Bairro, Cidade, UF, CEP",
        # )
        return
    
    # Salva antes de transicionar — dado precisa estar no banco quando o button_reply chegar
    prestador_manager.update_endereco(ctx_meta.phone, endereco)
    user_manager.update_state(ctx_meta.phone, EstadoUser.CADASTRO_ENDERECO)

    # send_msg_botao(
    #     phone=ctx_meta.phone,
    #     text=(
    #         f"📍 *Endereço informado:*\n\n"
    #         f"{endereco.logradouro}, {endereco.numero or 'S/N'}\n"
    #         f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
    #         f"CEP: {endereco.cep}\n\n"
    #         f"Está correto?"
    #     ),
    #     botoes=[
    #         BotaoResponse(id="endereco_confirmado", titulo="✅ Confirmar"),
    #         BotaoResponse(id="endereco_corrigir",   titulo="✏️ Corrigir"),
    #     ],
    # )