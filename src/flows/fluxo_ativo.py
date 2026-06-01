from src.services.ai_service import analisar_msg_nota_ai
from src.services.msg_service import enviar_mensagem
from src.repositories.nfse_db import adicionar_fila_emissao, atualizar_nf_parcial, buscar_nf_parcial, limpar_nf_parcial
from src.utils.validacao import normalizar_dados_nf, validar_dados_nf, mesclar_dados_nf
from src.types.context_nfse import ContextNfse, DadosNfse, Tomador, Servico, Valores

def fluxo_ativo(ctx: ContextNfse):

    print(f"\n\n----------------TESTE FLUXO ATIVO----------------\n\n")

    analisar_msg_nota_ai(ctx)

    # nome='ABBa LTDA'
    # cnpj='44555666000177'
    # descricao='marcenaria'
    # total=1500
    # aliquotaIss=3

    # ctx.dados_novos = DadosNfse(
    #         tomador=Tomador(
    #             nome=nome,
    #             cnpj=cnpj
    #         ),
    #         servico=Servico(
    #             descricao=descricao
    #         ),
    #         valores=Valores(
    #             total=total,
    #             aliquotaIss=aliquotaIss
    #         )
    #     )

    print(f"IA analisou ultima mensagem\ndados_novos: {ctx.dados_novos}\n")

    if ctx.dados_novos:

        atualizar_nf_parcial(ctx)
    
    buscar_nf_parcial(ctx)

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

    adicionar_fila_emissao(ctx)

    limpar_nf_parcial(ctx)

    # enviar_mensagem(
    #     phone,
    #     "text",
    #     "nota emitida com sucesso."
    # )

    print(f"MSG: Nota emitida com sucesso!\n")

    return "OK", 200