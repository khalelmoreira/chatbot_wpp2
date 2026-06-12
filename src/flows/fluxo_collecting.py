from src.services.ai_service import analisar_msg_nota_ai, extract_nf_gemma, has_intent, no_intent_response
from src.managers.tomador_manager import TomadorManager
from src.types.context_tomador import ContextTomador
from src.models.conversation_state import ConversationStatus
from src.services.validador_tomador import ValidadorTomador
from src.utils.debug import print_table
from src.services.msg_service import send_msg_text, send_msg_botao
from src.managers.conversation_manager import ConversationManager
from src.types.botoes_types import BotaoResponse
from src.utils.unpack_json import unpack_dados_db

def fluxo_collecting(ctx: ContextTomador, conversation: ConversationManager) -> None:
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")

    validador = ValidadorTomador()

    if ctx.conversation_id is None:
        intencao = has_intent(ctx)
        print(f"INTENCAO: {intencao}\n")

        if not intencao:
            response = no_intent_response(ctx)
            print(f"RESPONSE: {response}\n")
            #send_msg_text(ctx.user.phone, response)
            return
        ctx.conversation_id = conversation.create_conversation(ctx)

    else:
        intencao = has_intent(ctx)
        print(f"INTENCAO: {intencao}\n")
        
        if not intencao:
            response = no_intent_response(ctx)
            print(f"RESPONSE: {response}\n")
            #send_msg_text(ctx.user.phone, response)
            return
    

    extract_nf_gemma(ctx)
    print(f"DADOS NOVOS: {ctx.dados_novos}\n")

    draft = conversation.get_draft(ctx)
    print(f"DRAFT: {draft}\n")
    unpack_dados_db(draft, ctx)
    print(f"DADOS DRAFT:{ctx.dados_db}\n")

    ctx.dados_completos = ctx.dados_db.merge(ctx.dados_novos)
    print(f"MERGE: {ctx.dados_completos}\n")

    validador.validar(ctx)

    if ctx.validacao.validos:

        conversation.update_draft(ctx.conversation_id, ctx.validacao.validos)
        print(f"VALIDACAO: {ctx.validacao}\n")

        if not ctx.validacao.is_complete:

            pendencias = (ctx.validacao.invalidos + ctx.validacao.faltantes)
            #send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)
            print(f"pendencias: {pendencias}\n")
            return
        
        #SALVA NA FILA (nfs)
        conversation.update_draft(ctx.conversation_id, ctx.validacao.validos)
        conversation.update_state(ctx.conversation_id, ConversationStatus.CONFIRMING)

        # send_msg_botao(
        #     phone=ctx.user.phone,
        #     text=(
        #         f"*Dados do tomador:*\n\n"
        #         f"{ctx.dados_completos.tomador.nome}\n"
        #         f"{ctx.dados_completos.tomador.cnpj}\n"
        #         f"{ctx.dados_completos.servico.descricao}\n"
        #         f"{ctx.dados_completos.valores.total}\n"
        #         f"Esses dados estão corretos?"
        #     ),
        #     botoes=[
        #         BotaoResponse(id="tomador_confirmado", title="✅ Confirmar"),
        #         BotaoResponse(id="tomador_corrigir", title="✏️ Corrigir"),
        #     ],
        # )

        print(
            f"*Dados do tomador:*\n\n"
            f"{ctx.dados_completos.tomador.nome}\n"
            f"{ctx.dados_completos.tomador.cnpj}\n"
            f"{ctx.dados_completos.servico.descricao}\n"
            f"{ctx.dados_completos.valores.total}\n"
            f"Esses dados estão corretos?"
        )
        print_table(table_name="tomador", where=ctx.user.phone)
        
        return
        # print("dados completos\n")

        # tomador.add_fila(ctx)

        # tomador.delete_nfse_draft(ctx)

    
    print(f"SEM DADOS VALIDOS\nVALIDOS: {ctx.validacao.validos}\n")
    return