from datetime import datetime

from src.managers.nfs.nf_worker_manager import NfsWorkerManager


def _setup_stuck_job(db) -> int:
    phone = "5521991112222"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")
    conv_id = db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "QUEUED", "draft_json": "{}"},
        returning="id",
    )
    tomador_id = db.insert(
        "tomador", data={"prestador_id": prestador_id, "cnpj": "44555666000177", "name": "ABBa"}, returning="id"
    )
    return db.insert(
        "nfs",
        data={
            "prestador_id": prestador_id, "tomador_id": tomador_id, "conv_id": conv_id,
            "idempotency_key": f"key-{conv_id}", "status": "PROCESSING", "tentativas": 1,
            "payload_enviado": "{}", "nome": "ABBa", "cnpj": "44555666000177",
            "descricao_servico": "marcenaria", "valor_total": 1500.0,
            "processado_em": "2020-01-01 00:00:00",
        },
        returning="id",
    )


def test_resetar_jobs_travados_libera_job_preso_mesmo_sem_job_queued(db):
    """Reproduz um restart do servidor com o único job em PROCESSING (travado
    há mais de 5 min) e nenhum job QUEUED — reserva_job() sozinho nunca acharia
    esse job, então resetar_jobs_travados precisa poder rodar de forma
    independente (ver EmissaoWorker._loop)."""
    nfs_id = _setup_stuck_job(db)

    NfsWorkerManager.resetar_jobs_travados()

    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "QUEUED"

    manager = NfsWorkerManager.reserva_job()
    assert manager is not None
    assert manager.jid == nfs_id


def test_resetar_jobs_travados_ignora_job_processing_recente(db):
    phone = "5521991112222"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")
    conv_id = db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "QUEUED", "draft_json": "{}"},
        returning="id",
    )
    tomador_id = db.insert(
        "tomador", data={"prestador_id": prestador_id, "cnpj": "44555666000177", "name": "ABBa"}, returning="id"
    )
    nfs_id = db.insert(
        "nfs",
        data={
            "prestador_id": prestador_id, "tomador_id": tomador_id, "conv_id": conv_id,
            "idempotency_key": f"key-{conv_id}", "status": "PROCESSING", "tentativas": 1,
            "payload_enviado": "{}", "nome": "ABBa", "cnpj": "44555666000177",
            "descricao_servico": "marcenaria", "valor_total": 1500.0,
            "processado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        returning="id",
    )

    NfsWorkerManager.resetar_jobs_travados()

    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "PROCESSING"
