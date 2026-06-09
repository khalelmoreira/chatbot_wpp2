from src.flows.fluxo_prestador import fluxo_prestador
from src.flows.fluxo_ativo import fluxo_ativo
from src.flows.fluxo_endereco import fluxo_endereco
from src.flows.fluxo_endereco_manual import fluxo_endereco_manual
from src.managers.user_manager import UserManager
from src.services.msg_service import send_msg_text, send_msg_botao
from src.types.incoming_msg import IncomingMessage
from src.types.context_prestador import ContextPrestador, DadosPrestador
from src.types.context_tomador import ContextTomador, DadosTomador
from src.utils.debug import print_table
from src.types.estado_user import EstadoUser

def fluxo_principal(ctx_meta: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO PRINCIPAL----------------\n\n")

    phone = ctx_meta.phone
    text = ctx_meta.text
    user_manager = UserManager()
    user = user_manager.get_user(phone)

    print_table(table_name="users", where=phone)

    if not user:
        
        user = user_manager.criar_user(ctx_meta)

        print(f"USER CRIADO:\n")
        print_table(table_name="users", where=phone)

        # send_msg_text(
        #     phone,
        #     "Olá! Seja bem-vindo à automação de notas fiscais.\n\n"
        #     "Para começar, me informe:\n"
        #     "- Razão social\n- CNPJ\n- E-mail\n- Regime tributário\n- CEP\n- Inscrição municipal"
        # )

        print(
            f"Olá! Seja bem-vindo à automação de notas fiscais.\n\n"
            "Para começar, me informe:\n"
            "- Razão social\n- CNPJ\n- E-mail\n- Regime tributário\n- CEP\n- Inscrição municipal"
            )
        return
    
    estado = EstadoUser(user.estado)

    match estado:

        case EstadoUser.NOVO:
            #send_msg_text(phone, "Vamos iniciar seu cadastro...")
            user_manager.update_state(user, EstadoUser.CADASTRO_PRESTADOR)
            return

        case EstadoUser.CADASTRO_PRESTADOR:

            ctx = ContextPrestador(
            user=user,
            text=text,
            dados_novos=DadosPrestador(),
            dados_db=DadosPrestador(),
            dados_completos=DadosPrestador(),
        )
            return fluxo_prestador(ctx, user_manager)
        
        case EstadoUser.CADASTRO_ENDERECO:
            return fluxo_endereco(ctx_meta, user_manager)
        
        case EstadoUser.CADASTRO_ENDERECO_MANUAL:
            return fluxo_endereco_manual(ctx_meta, user_manager)
        
        case EstadoUser.CRIANDO_PROJETO_NOTAAS:

            print("ok")
           #send_msg_text(phone, "Ainda estamos configurando sua conta, aguarde um momento.")

        case EstadoUser.ATIVO:

            ctx = ContextTomador(
            user=user,
            text=text,
            dados_novos=DadosTomador(),
            dados_db=DadosTomador(),
            dados_completos=DadosTomador(),
        )
            return fluxo_ativo(ctx)
    
        case _:

            raise ValueError(f"Estado não mapeado no fluxo: {user.estado}")