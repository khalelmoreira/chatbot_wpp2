from src.services.ai_service import analisar_mensagem_ia
from src.repositories.user_db import UserManager
from src.utils.validacao import validar_dados_mensagem
from src.services.msg_service import enviar_mensagem
from src.types.context_cadastro import ContextCadastro

def fluxo_cadastro(ctx: ContextCadastro):
        
        print(f"\n\n----------------TESTE FLUXO CADASTRO----------------\n\n")

        analisar_mensagem_ia(ctx)
        print(f"IA analisou ultima mensagem: {ctx.dados_novos}\n")

        user_manager = UserManager()

        if ctx.dados_novos:

            user_manager.update_draft(ctx)

        user_manager.get_draft(ctx)

        validar_dados_mensagem(ctx)

        if not ctx.validacao.is_valido:
            
            pendencias = (
                ctx.validacao.invalidos +
                ctx.validacao.faltantes
            )

            print(f"pendencias: {pendencias}\n")

            # enviar_mensagem(
            #     ctx.user.phone,
            #     "text",
            #     "Parece que ficou faltando esses dados:",
            #     pendencias
            # )

            print(f"MSG: Parece que ficou faltando alguns dados: {pendencias}\n")

            return
        
        print("Dados válidos! Todos os dados completos!\nUSUARIO ATIVO\n")

        # enviar_mensagem(
        #     ctx.user.phone,
        #     "text",
        #     "Todos os dados já estão completos. Podemos começar!"
        # )

        print(f"MSG: Todos os dados já estão completos. Podemos começar!\n")

        user_manager.update_draft(ctx.user, "ativo")