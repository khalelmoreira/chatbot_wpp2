from src.services.ai_service import analisar_msg_nota_ai, extract_nf_gemma, has_intent, no_intent_response
from src.managers.tomador_manager import TomadorManager
from src.types.context_tomador import ContextTomador
from src.models.conversation_state import ConversationStatus
from src.services.validador_tomador import ValidadorTomador
from src.utils.debug import print_table
from src.services.msg_service import send_msg_text
from src.managers.conversation_manager import ConversationManager

def fluxo_collecting(ctx: ContextTomador, conversation: ConversationManager):
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")

    tomador = TomadorManager()
    validador = ValidadorTomador()

    if ctx.conversation_id is None:
        intencao = has_intent(ctx)

        if not intencao:
            response = no_intent_response(ctx)
            send_msg_text(ctx.user.phone, response)
            return
        
        ctx.conversation_id = conversation.create_conversation(ctx.user.phone, ctx.user.id)
    

    extract_nf_gemma(ctx)
    print(f"DADOS NOVOS: {ctx.dados_novos}\n")

    conversation.get_draft(ctx.conversation_id)
    print(f"DADOS DRAFT:{ctx.dados_db}\n")

    ctx.dados_completos = ctx.dados_db.merge(ctx.dados_novos)
    print(f"MERGE: {ctx.dados_completos}\n")

    validador.validar(ctx)

    if ctx.validacao.validos:

        conversation.update_draft(ctx.conversation_id, ctx.validacao.validos)
        print(f"VALIDACAO: {ctx.validacao}\n")

        if not ctx.validacao.is_complete:

            pendencias = (ctx.validacao.invalidos + ctx.validacao.faltantes)
            colunas = ["id", "prestador_id", "tomador_id", "idempotency_key", "status", "nome", "cnpj", "descricao_servico", "aliquota_iss", "valor_total"]

            print(f"pendencias: {pendencias}\n")
            print(f"DADOS DB ATUAL:")
            print_table(table_name="tomador", columns=colunas, where=ctx.user.phone)

            #send_msg_text(ctx.user.phone, "Parece que ficou faltando esses dados:", pendencias)

            return
        
        tomador.update_nf_from_draft(ctx)
        conversation.update_state(ctx.conversation_id, ConversationStatus.CONFIRMING)
        
        return
        print("dados completos\n")

        tomador.add_fila(ctx)

        tomador.delete_nfse_draft(ctx)

    
    print(f"SEM DADOS VALIDOS\nVALIDOS: {ctx.validacao.validos}\n")
    return