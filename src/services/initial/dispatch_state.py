from src.types.estado_user import EstadoUser
from src.managers.user_manager import UserManager
from src.types.context_base import User
from src.types.context_prestador import ContextPrestador, DadosPrestador
from src.types.context_tomador import ContextTomador, DadosTomador
from src.types.incoming_msg import IncomingMessage
from src.flows.fluxo_prestador import fluxo_prestador
from src.services.core.dispatch_active_state import dispatch_active_state
from src.flows.fluxo_endereco import fluxo_endereco
from src.flows.fluxo_endereco_manual import fluxo_endereco_manual

def dispatch_state(user_manager: UserManager, user: User, msg: IncomingMessage):

    estado = EstadoUser(user.estado)

    match estado:

        case EstadoUser.NOVO:
            #send_msg_text(phone, "Vamos iniciar seu cadastro...")
            user_manager.update_state(user, EstadoUser.CADASTRO_PRESTADOR)
            return

        case EstadoUser.CADASTRO_PRESTADOR:

            ctx = ContextPrestador(
            user=user,
            text=msg.text,
            dados_novos=DadosPrestador(),
            dados_db=DadosPrestador(),
            dados_completos=DadosPrestador(),
        )
            return fluxo_prestador(ctx, user_manager)
        
        case EstadoUser.CADASTRO_ENDERECO:
            return fluxo_endereco(msg, user_manager)
        
        case EstadoUser.CADASTRO_ENDERECO_MANUAL:
            return fluxo_endereco_manual(msg, user_manager)
        
        case EstadoUser.CRIANDO_PROJETO_NOTAAS:

            print("ok")
        #send_msg_text(phone, "Ainda estamos configurando sua conta, aguarde um momento.")

        case EstadoUser.ATIVO:
                
            ctx = ContextTomador(
            user=user,
            text=msg.text,
            dados_novos=DadosTomador(),
            dados_db=DadosTomador(),
            dados_completos=DadosTomador(),
        )
            return dispatch_active_state(ctx, msg)
    
        case _:

            raise ValueError(f"Estado não mapeado no fluxo: {user.estado}")