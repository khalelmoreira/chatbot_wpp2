from src.types.incoming_msg import IncomingMessage
from src.types.context_base import User
from src.managers.user_manager import UserManager
from src.utils.debug import print_table

def user_exists(msg: IncomingMessage, user_manager: UserManager) -> User:

        user = user_manager.get_user(msg.phone)
        print_table(table_name="users", where=msg.phone)

        if not user:
            
            user = user_manager.criar_user(msg)
            print(f"USER CRIADO:\n")
            print_table(table_name="users", where=msg.phone)

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
            return user
        
        return user