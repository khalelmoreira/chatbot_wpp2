from dataclasses import fields
from src.managers.user_manager import UserManager
from src.types.incoming_msg import IncomingMessage
from src.types.estado_user import EstadoUser
from src.managers.prestador_manager import PrestadorManager
from src.services.ai_service import extract_endereco_gemma
from src.services.msg_service import send_msg_text, send_msg_botao
from src.types.botoes_types import BotaoResponse

def fluxo_endereco_manual(
        msg: IncomingMessage,
        user_manager: UserManager
):
    
    prestador_manager = PrestadorManager()
    endereco = extract_endereco_gemma(msg.text)

    if endereco is None:
        # send_msg_text(
        #     msg.phone,
        #     "Não consegui identificar o endereço. Tente no formato:\n\n"
        #     "Logradouro, Número, Bairro, Cidade, UF, CEP",
        # )
        print(
            "Não consegui identificar o endereço. Tente no formato:\n\n"
            "Logradouro, Número, Bairro, Cidade, UF, CEP e completemento se houver"
        )
        return
    
    campos_faltantes = [
        f.name for f in fields(endereco)
        if f.name in {"logradouro", "bairro", "cidade", "uf", "cep"}
        and getattr(endereco, f.name) is None
    ]
    
    if campos_faltantes:
        # send_msg_text(
        #     msg.phone,
        #     f"Parece que ficou faltando esses campos {', '.join(campos_faltantes)} envie-os para terminarmos seu cadasto.",
        # )
        print(f"Parece que ficou faltando esses campos {campos_faltantes} envie-os para terminarmos seu cadasto.")

        return
    
    # Salva antes de transicionar — dado precisa estar no banco quando o button_reply chegar
    prestador_manager.update_endereco(msg.phone, endereco)
    user_manager.update_state(msg.phone, EstadoUser.CADASTRO_ENDERECO)

    # send_msg_botao(
    #     phone=msg.phone,
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

    print(
        f"📍 *Endereço informado:*\n\n"
        f"{endereco.logradouro}, {endereco.numero or 'S/N'}\n"
        f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
        f"CEP: {endereco.cep}\n\n"
        f"Está correto?"
    )