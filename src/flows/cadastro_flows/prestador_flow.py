from src.types import ContextPrestador, EstadoUser, BotaoResponse
from src.managers.prestador.prestador_manager import PrestadorManager
from src.managers.users.user_manager import UserManager
from src.services.shared.msg_service import WhatsAppService
from src.services.validators.validador_prestador import ValidadorPrestador
from src.utils.debug import print_table
from src.utils.get_endereco import get_endereco_by_cep

def prestador_flow(ctx: ContextPrestador, user_manager: UserManager):
        
        prestador = PrestadorManager()
        validador = ValidadorPrestador()
        wpp = WhatsAppService()
        
        print(f"\n\n----------------TESTE FLUXO PRESTADOR----------------\n\n")

        extract_data_prestador_gemma(ctx)
        print(f"DADOS NOVOS: {ctx.dados_novos}\n")


        prestador.get_db_data(ctx)
        print(f"DADOS DO DB: {ctx.dados_db}\n")

        ctx.dados_completos = ctx.dados_db.merge(ctx.dados_novos)
        print(f"MERGE: {ctx.dados_completos}\n")


        validador.validar(ctx)

        if ctx.validacao.validos:

            prestador.update_validos(ctx)
            print(f"VALIDACAO: {ctx.validacao}\n")

            if not ctx.validacao.is_complete:
            
                pendencias = (ctx.validacao.invalidos + ctx.validacao.faltantes)

                print(f"pendencias: {pendencias}\n")
                print(f"DADOS DB ATUAL:")
                print_table(table_name="prestador", where=ctx.user.phone)

                #wpp.send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)

                return
        
            cep = ctx.dados_completos.cep
            print(f"CEP: {cep}\n")

            endereco = get_endereco_by_cep(cep)
            print(f"ENDERECO: {endereco}\n")

            if endereco is None:
                #wpp.send_msg_text(ctx.user.phone, f"Não consegui encontrar o endereço para o CEP {cep}.\nPode verificar e enviar novamente?")
                print(f"Não consegui encontrar o endereço para o CEP {cep}.\nPode verificar e enviar novamente?\n")
                return

            user_manager.update_state(ctx.user.phone, EstadoUser.CADASTRO_ENDERECO)

            # wpp.send_msg_botao(
            #     phone=ctx.user.phone,
            #     text=(
            #         f"📍 *Endereço encontrado:*\n\n"
            #         f"{endereco.logradouro}\n"
            #         f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
            #         f"CEP: {endereco.cep}\n\n"
            #         f"Esse é o endereço correto?"
            #     ),
            #     botoes=[
            #         BotaoResponse(id="endereco_confirmado", title="✅ Confirmar"),
            #         BotaoResponse(id="endereco_corrigir", title="✏️ Corrigir"),
            #     ],
            # )

            print(
                f"📍 *Endereço encontrado:*\n\n"
                f"{endereco.logradouro}\n"
                f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
                f"CEP: {endereco.cep}\n\n"
                f"Esse é o endereço correto?\n"
            )

            print_table(table_name="users", where=ctx.user.phone)

            return

        print(f"SEM DADOS VALIDOS\nVALIDOS: {ctx.validacao.validos}\n")
        return