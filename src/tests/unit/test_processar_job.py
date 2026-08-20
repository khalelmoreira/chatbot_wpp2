import src.services.worker.processar_job as processar_job_module
from src.managers.nfs.nf_worker_manager import NfsWorkerManager
from src.services.worker.processar_job import processar_job
from src.types import NotaasEmissaoPermanenteError, NotaasEmissaoTransitoriaError


def _setup_job(db, tentativas: int = 0) -> tuple[int, int, int]:
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
            "idempotency_key": f"key-{conv_id}", "status": "QUEUED", "tentativas": tentativas,
            "payload_enviado": "{}", "nome": "ABBa", "cnpj": "44555666000177",
            "descricao_servico": "marcenaria", "valor_total": 1500.0,
        },
        returning="id",
    )
    return prestador_id, conv_id, nfs_id


def test_erro_permanente_encerra_job_sem_retry_e_notifica(db, monkeypatch):
    prestador_id, conv_id, nfs_id = _setup_job(db)
    manager = NfsWorkerManager.reserva_job()
    assert manager is not None

    def _raise(*a, **kw):
        raise NotaasEmissaoPermanenteError("payload rejeitado")

    monkeypatch.setattr(processar_job_module, "emitir_nf", _raise)
    espera = processar_job(manager)

    assert espera is None
    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "ERROR"

    conv = db.select_one("conversations", where={"id": conv_id})
    assert conv["status"] == "ERROR"

    msgs = db.select("messages", where={"prestador_id": prestador_id})
    assert any("rejeitou" in m["content"].lower() for m in msgs)


def test_erro_transitorio_reenfileira_sem_notificar_antes_do_limite(db, monkeypatch):
    _, _, nfs_id = _setup_job(db, tentativas=0)
    manager = NfsWorkerManager.reserva_job()
    assert manager is not None

    def _raise(*a, **kw):
        raise NotaasEmissaoTransitoriaError("timeout")

    monkeypatch.setattr(processar_job_module, "emitir_nf", _raise)
    espera = processar_job(manager)

    assert espera is not None
    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "QUEUED"


def test_erro_transitorio_no_limite_marca_error_e_notifica(db, monkeypatch):
    prestador_id, conv_id, nfs_id = _setup_job(db, tentativas=2)  # reserva_job leva a 3 == MAX_TENTATIVAS
    manager = NfsWorkerManager.reserva_job()
    assert manager is not None

    def _raise(*a, **kw):
        raise NotaasEmissaoTransitoriaError("indisponivel")

    monkeypatch.setattr(processar_job_module, "emitir_nf", _raise)
    processar_job(manager)

    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "ERROR"

    conv = db.select_one("conversations", where={"id": conv_id})
    assert conv["status"] == "ERROR"

    msgs = db.select("messages", where={"prestador_id": prestador_id})
    assert any("indisponível" in m["content"].lower() or "tentativas" in m["content"].lower() for m in msgs)
