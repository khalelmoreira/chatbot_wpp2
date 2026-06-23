from src.types import IncomingMessage, User
from src.managers.users.user_manager import UserManager
from src.services.shared.msg_service import WhatsAppService
from src.utils.debug import print_table

def user_exists(msg: IncomingMessage, user_manager: UserManager) -> User:

        wpp = WhatsAppService()
        user = user_manager.get_user()
        print_table(table_name="users", where=msg.phone)

        if not user:
            
            user = user_manager.criar_user(msg)
            print(f"USER CRIADO:\n")
            print_table(table_name="users", where=msg.phone)

            # wpp.send_msg_text(
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