from src.services.ai_service import extract_data_prestador, extract_data_prestador_gemma
from src.managers.prestador_manager import PrestadorManager
from src.repositories.user_db import UserManager
from src.services.msg_service import enviar_mensagem
from src.types.context_prestador import ContextPrestador
from src.managers.validacao_manager import ValidadorPrestadorManager
from src.utils.debug import print_table

def fluxo_prestador(ctx: ContextPrestador):
        
        print(f"\n\n----------------TESTE FLUXO CADASTRO----------------\n\n")

        extract_data_prestador_gemma(ctx)

        print(f"DADOS NOVOS (ULTIMA MENSAGEM): {ctx.dados_novos}\n")

        prestador = PrestadorManager()

        # LE ESTADO ATUAL DO DB

        prestador.get_db_data(ctx)

        print(f"PEGOU OS DADOS DO DB: {ctx.dados_db}\n")

        # MERGE = NOVOS + DB

        ctx.dados_completos = ctx.dados_db.merge(ctx.dados_novos)

        print(f"MERGE: {ctx.dados_completos}\n")

        validador = ValidadorPrestadorManager()

        validador.validar(ctx)

        # SALVA VALIDOS NO DB
        prestador.update_validos(ctx)

        print(f"VALIDACAO: {ctx.validacao}\n")

        if not ctx.validacao.is_complete:
            
            pendencias = (
                ctx.validacao.invalidos +
                ctx.validacao.faltantes
            )

            print(f"pendencias: {pendencias}\n")
            print(f"DADOS DB ATUAL\n")
            print_table(
                table_name="prestador",
                where=ctx.user.phone
                )

            # enviar_mensagem(
            #     ctx.user.phone,
            #     "text",
            #     "Parece que ficou faltando esses dados:",
            #     pendencias
            # )

            print(f"MSG: Parece que ficou faltando alguns dados: {pendencias}\n")

            return

        print(f"DADOS DB ATUAL:\n")
        print_table(
                table_name="prestador",
                where=ctx.user.phone
                )

        print("Dados válidos! Todos os dados completos!\nUSUARIO ATIVO\n")

        # enviar_mensagem(
        #     ctx.user.phone,
        #     "text",
        #     "Todos os dados já estão completos. Podemos começar!"
        # )

        user = UserManager()

        user.update_status(ctx.user, "ativo")

        print_table(
                table_name="users",
                where=ctx.user.phone
                )
        
        return