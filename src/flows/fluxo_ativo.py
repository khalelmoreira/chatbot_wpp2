from src.services.ai_service import analisar_msg_nota_ai, extract_nf_gemma
from src.managers.tomador_manager import TomadorManager
from src.types.context_tomador import ContextTomador, DadosTomador, Tomador, Servico, Valores
from src.services.validador_tomador import ValidadorTomador
from src.utils.debug import print_table

def fluxo_ativo(ctx: ContextTomador):
    
    tomador = TomadorManager()
    validador = ValidadorTomador()

    print(f"\n\n----------------TESTE FLUXO ATIVO----------------\n\n")

    extract_nf_gemma(ctx)
    print(f"DADOS NOVOS: {ctx.dados_novos}\n")


    tomador.get_db_data(ctx)
    print(f"DADOS DB:{ctx.dados_db}\n")


    ctx.dados_completos = ctx.dados_db.merge(ctx.dados_novos)
    print(f"MERGE: {ctx.dados_completos}\n")


    validador.validar(ctx)

    if ctx.validacao.validos:

        tomador.update_validos(ctx)
        print(f"VALIDACAO: {ctx.validacao}\n")

        if not ctx.validacao.is_complete:

            pendencias = (ctx.validacao.invalidos + ctx.validacao.faltantes)
            colunas = ["id", "prestador_id", "tomador_id", "idempotency_key", "status", "nome", "cnpj", "descricao_servico", "aliquota_iss", "valor_total"]

            print(f"pendencias: {pendencias}\n")
            print(f"DADOS DB ATUAL:")
            print_table(table_name="tomador", columns=colunas, where=ctx.user.phone)

            #send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)

            return
        
    print(f"SEM DADOS VALIDOS\nVALIDOS: {ctx.validacao.validos}\n")
    return

    print("dados completos\n")

    tomador.add_fila(ctx)

    tomador.delete_nfse_draft(ctx)

    return "OK", 200