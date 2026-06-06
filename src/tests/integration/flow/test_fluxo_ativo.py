from src.database.db import init_db, executar_modif, buscar_nf_parcial
from src.tests.generators.gen_msg_ai import gen_msg_fake, gen_conversa_fake
#from app.services.ai_service import analisar_msg_nota_ai
from src.flows.fluxo_ativo import fluxo_ativo
#from app.functions.validacao import normalizar_dados_nf, validar_dados_nf
from src.tests.unit.test_processar_job import processar_job, print_fila


# def test_fluxo_ativo_split():

#     qtd = 10

#     mensagens = gen_msg_fake(
#         tipo="nfse",
#         quantidade=qtd
#     )

#     # ==========================================
#     # TESTE GERADOR
#     # ==========================================

#     assert mensagens is not None, (
#         "gen_msg_fake retornou None"
#     )

#     assert isinstance(mensagens, list), (
#         f"Esperado list, recebido {type(mensagens)}"
#     )

#     assert len(mensagens) == qtd, (
#         f"Esperado {qtd} mensagens, recebido {len(mensagens)}"
#     )

#     # ==========================================
#     # LOOP PRINCIPAL
#     # ==========================================

#     for i, mensagem in enumerate(mensagens):

#         print("\n" + "=" * 60)
#         print(f"CASO {i+1}")
#         print("=" * 60)

#         print(f"\nMENSAGEM:\n{mensagem}\n")

#         # ==========================================
#         # TESTE EXTRAÇÃO IA
#         # ==========================================

#         dados_extraidos = analisar_msg_nota_ai(
#             mensagem
#         )

#         print(f"DADOS EXTRAIDOS:\n{dados_extraidos}\n")

#         assert dados_extraidos is not None, (
#             f"Extração IA retornou None\n"
#             f"Mensagem: {mensagem}"
#         )

#         assert isinstance(dados_extraidos, dict), (
#             f"Esperado dict na extração IA, "
#             f"recebido {type(dados_extraidos)}\n"
#             f"Mensagem: {mensagem}"
#         )

#         # ==========================================
#         # TESTE NORMALIZAÇÃO
#         # ==========================================

#         dados_normalizados = normalizar_dados_nf(
#             dados_extraidos
#         )

#         print(
#             f"DADOS NORMALIZADOS:\n"
#             f"{dados_normalizados}\n"
#         )

#         assert dados_normalizados is not None, (
#             f"Normalização retornou None\n"
#             f"Mensagem: {mensagem}"
#         )

#         assert isinstance(dados_normalizados, dict), (
#             f"Esperado dict na normalização, "
#             f"recebido {type(dados_normalizados)}\n"
#             f"Mensagem: {mensagem}"
#         )

#         # ==========================================
#         # TESTE VALIDAÇÃO
#         # ==========================================

#         dados_validados = validar_dados_nf(
#             dados_normalizados
#         )

#         print(
#             f"RESULTADO VALIDAÇÃO:\n"
#             f"{dados_validados}\n"
#         )

#         assert dados_validados is not None, (
#             f"Validação retornou None\n"
#             f"Mensagem: {mensagem}"
#         )

#         assert isinstance(dados_validados, list), (
#             f"Esperado list na validação, "
#             f"recebido {type(dados_validados)}\n"
#             f"Mensagem: {mensagem}"
#         )

#         print("TESTE OK")
    
#     return

def test_fluxo_ativo():

    qtd = 10
    init_db()

    for i in range(qtd):

        phone = f"22999999999{i}"
        user_text = gen_msg_fake(tipo="nfse", quantidade=1)

        print(f"\nmensagem: {user_text}\n")

        user = {
            "estado": "ativo"
        }

        fluxo_ativo(phone, user_text, user)

        jobs = executar_modif(
            """
        SELECT *
        FROM fila_emissao
        WHERE status = 'pendente'
        ORDER BY id
        """,
        fetchall=True
        )

        for job in jobs:

            processar_job(job)

        job_processado = executar_modif(
            """
        SELECT *
        FROM fila_emissao
        WHERE status = 'emitido'
        """,
        fetchall=True
        )

        print_fila()

        assert job_processado["status"] == "emitido"

def test_conversa_ativa():

    init_db()

    conversas = gen_conversa_fake(
        tipo="nfse",
        num_conversas=3,
        turnos_conversa=(2, 4)
    )

    total_emitidas = 0

    for i, conversa in enumerate(conversas):

        phone = f"22999999999{i}"

        user = {
            "estado": "ativo"
        }

        print(f"\n======== CONVERSA {i+1} ========\n")

        for turno, msg in enumerate(conversa):

            print(f"[{turno+1}] {msg}\n")

            fluxo_ativo(phone, msg, user)

            nf_parcial = buscar_nf_parcial(phone)

            print(f"NF parcial atual: {nf_parcial}\n")

        jobs_pendentes = executar_modif(
            """
            SELECT *
            FROM fila_emissao
            WHERE phone = ?
            AND status = 'pendente'
            """,
            (phone,),
            fetchall=True
        )

        if jobs_pendentes:
            assert len(jobs_pendentes) == 1

            job = jobs_pendentes[0]

            processar_job(job)

            job_emitido = executar_modif(
                """
                SELECT *
                FROM fila_emissao
                WHERE id = ?
                """,
                (job["id"],),
                fetchone=True
            )

            assert job_emitido["status"] == "emitido"

            nf_parcial = buscar_nf_parcial(phone)

            assert not nf_parcial

            total_emitidas += 1
        
        else:
            print("conversa imcompleta, nenhuma emissao\n")

            nf_parcial = buscar_nf_parcial(phone)

            assert nf_parcial is not None
    
    print_fila()

    assert total_emitidas > 0