import json
import time
from src.database.db import marcar_processamento, marcar_emitido, marcar_erro, executar_modif
from chatbot_wpp2.src.services.shared.emission_service import emitir_nf

def processar_job(job):

    try:

        marcar_processamento(job["id"])
        print("status updated processando job...\n")

        payload = json.loads(job["payload"])
        
        nota = emitir_nf(payload)
        print(f"nota emitida: {nota}\n")

        marcar_emitido(job["id"])
        print("status updated emitido\n")

        time.sleep(10)

        return True

    except Exception as e:

        marcar_erro(job["id"], e)
        time.sleep(15)

        return False
    
def print_fila():

    jobs = executar_modif(
        """
        SELECT
            id,
            status,
            tentativas,
            processado_em
        FROM fila_emissao
        ORDER BY id
        """,
        fetchall=True
    )

    print("\n===== FILA EMISSAO =====")

    for job in jobs:

        print(
            f"""
            ID: {job['id']}
            STATUS: {job['status']}
            TENTATIVAS: {job['tentativas']}
            PROCESSADO_EM: {job['processado_em']}
            -------------------------
            """
        )