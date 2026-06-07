from src.services.ai_service import analisar_msg_nota_ai
from src.managers.nfse_manager import NFSeManager
from src.utils.validacao import normalizar_dados_nf, validar_dados_nf
from src.types.context_nfse import ContextNfse, DadosNfse, Tomador, Servico, Valores

def fluxo_ativo(ctx: ContextNfse):

    print(f"\n\n----------------TESTE FLUXO ATIVO----------------\n\n")

    analisar_msg_nota_ai(ctx)

    print(f"IA analisou ultima mensagem\ndados_novos: {ctx.dados_novos}\n")

    nfse_manager = NFSeManager()

    if ctx.dados_novos:

        nfse_manager.update_draft(ctx)
    
    nfse_manager.get_draft(ctx)

    print(f"dados_db:{ctx.dados_db}\n")

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

    nfse_manager.add_fila(ctx)

    nfse_manager.delete_nfse_draft(ctx)

    # enviar_mensagem(
    #     phone,
    #     "text",
    #     "nota emitida com sucesso."
    # )

    print(f"MSG: Nota emitida com sucesso!\n")

    return "OK", 200