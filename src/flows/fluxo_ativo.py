from src.services.ai_service import analisar_msg_nota_ai, extract_nf_gemma
from chatbot_wpp2.src.managers.tomador_manager import TomadorManager
from chatbot_wpp2.src.services.validador_tomador import normalizar_dados_nf, validar_dados_nf
from chatbot_wpp2.src.types.context_tomador import ContextTomador, DadosTomador, Tomador, Servico, Valores
from src.services.validador_tomador import ValidadorTomador

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

    tomador.update_draft(ctx)
    

    normalizar_dados_nf(ctx)

    print(f"NORMALIZOU: {ctx.dados_normalizados}\n")
    
    validar_dados_nf(ctx)

    print(f"VALIDADOR DEVOLVE: {ctx.validacao.validos}\n")

    if not ctx.validacao.is_valido:

        pendencias = (
            ctx.validacao.invalidos +
            ctx.validacao.faltantes
        )
        
        print(f"pendencias {pendencias}")

        # enviar_mensagem(
        #     ctx.user.phone,
        #     "text",
        #     "Parece que ficou faltando alguns dados:",
        #     pendencias
        # )

        print(f"MSG: Parece que ficou faltando alguns dados: {pendencias}\n")
        

    print("dados completos\n")

    tomador.add_fila(ctx)

    tomador.delete_nfse_draft(ctx)

    # enviar_mensagem(
    #     phone,
    #     "text",
    #     "nota emitida com sucesso."
    # )

    print(f"MSG: Nota emitida com sucesso!\n")

    return "OK", 200