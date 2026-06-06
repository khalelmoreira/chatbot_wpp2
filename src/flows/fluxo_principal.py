from src.flows.fluxo_prestador import fluxo_prestador
from src.flows.fluxo_ativo import fluxo_ativo
from src.repositories.user_db import UserManager
from src.services.msg_service import enviar_mensagem
from src.types.incoming_msg import IncomingMessage
from src.types.context_prestador import ContextPrestador, DadosPrestador
from src.types.context_nfse import ContextNfse, DadosNfse
from src.utils.debug import print_table

def fluxo_principal(ctx_meta: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO PRINCIPAL----------------\n\n")

    phone = ctx_meta.phone
    text = ctx_meta.text

    user_manager = UserManager()

    user = user_manager.get_user(phone)

    print(f"USER:\n")
    print_table(table_name="users", where=phone)

    if not user:
        
        user = user_manager.criar_user(phone)

        print(f"USER CRIADO:\n")
        print_table(table_name="users", where=phone)

        # enviar_mensagem(
        #     phone,
        #     "text",
        #         "Olá, seja muito bem vindo a sua IA para automação de notas fiscais.\n\n"
        #         "Para iniciarmos, envie os seguintes dados:\n"
        #         "- Nome completo\n"
        #         "- CPF ou CNPJ\n"
        #         "- E-mail\n\n"
        #         "Fico no aguardo!"
        # )

        print(
            f"MSG: Olá, seja muito bem vindo a sua IA para automação de notas fiscais.\n\n"
            "Para iniciarmos, envie os seguintes dados:\n"
            "- Nome completo\n"
            "- CPF ou CNPJ\n"
            "- E-mail\n\n"
            "Fico no aguardo!\n"
            )
        return
    
    if user.estado == "cadastro_prestador" or user.estado == "novo":

        ctx = ContextPrestador(
            user=user,
            text=text,
            dados_novos=DadosPrestador(),
            dados_db=DadosPrestador(),
            dados_completos=DadosPrestador(),
        )

        print(f"CTX CADASTRO: {ctx}\n")
        
        return fluxo_prestador(ctx)

    else:

        ctx = ContextNfse(
            user=user,
            text=text,
            dados_novos=DadosNfse(),
            dados_db=DadosNfse(),
            dados_completos=DadosPrestador(),
        )

        print(f"CTX NFSE: {ctx}\n")

        return fluxo_ativo(ctx)
