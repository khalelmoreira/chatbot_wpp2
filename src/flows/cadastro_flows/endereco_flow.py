from src.managers.users.user_manager import UserManager
from src.types import IncomingMessage, EstadoUser
from src.flows.active_flows.onboarding_flow import criar_project
from src.services.wpp.msg_service import WhatsAppService

def endereco_flow(
        msg: IncomingMessage,
        user_manager: UserManager,
) -> None:
    
    wpp = WhatsAppService()
    
    if msg.tipo != "button":
        #wpp.send_msg_text(msg.phone, "Por favor, use os botões para confirmar ou corrigir o endereço.")
        print(f"Por favor, use os botões para confirmar ou corrigir o endereço.\n")
        return
    
    if msg.id_botao == "endereco_corrigir":
        user_manager.update_state(msg.phone, EstadoUser.CADASTRO_ENDERECO_MANUAL)
        # wpp.send_msg_text(
        #     msg.phone,
        #     "Sem problema. Por favor, envie seu endereço completo no seguinte formato:\n\n"
        #     "Logradouro, Número, Bairro, Cidade, UF, CEP",
        #     )
        print(
            "Sem problema. Por favor, envie seu endereço completo no seguinte formato:\n\n"
            "Logradouro, Número, Bairro, Cidade, UF, CEP\n"
        )
        return
    
    if msg.id_botao == "endereco_confirmado":
        user_manager.update_state(msg.phone, EstadoUser.CRIANDO_PROJETO_NOTAAS)
        user_manager.update_state(msg.phone, EstadoUser.ATIVO)

        print("USER ATIVO!\n")
        
        resultado = criar_project(msg.phone)
    
        if not resultado.sucesso:
            # Estado fica em CRIANDO_PROJETO_NOTAAS — permite retry
            # wpp.send_msg_text(
            #     msg.phone,
            #     "Ocorreu um erro ao configurar sua conta. "
            #     "Tente novamente em instantes.",
            # )
            print(
                "Ocorreu um erro ao configurar sua conta. "
                "Tente novamente em instantes.\n"
            )
            return
        
        user_manager.update_state(msg.phone, EstadoUser.AGUARDANDO_CERTIFICADO)
        # wpp.send_msg_text(
        #     msg.phone,
        #     "✅ Conta configurada com sucesso!\n\n"
        #     "O último passo é o envio do seu certificado digital (.pfx).\n"
        #     "Você receberá um link para fazer o upload em breve.",
        # )
        print(
            "✅ Conta configurada com sucesso!\n\n"
            "O último passo é o envio do seu certificado digital (.pfx).\n"
            "Você receberá um link para fazer o upload em breve.\n"
        )