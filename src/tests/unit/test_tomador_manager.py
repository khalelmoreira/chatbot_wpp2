import pytest

from src.managers.tomador_manager import TomadorManager
from src.types import ContextTomador, InvalidTransactionError, MsgType, TomadorData, User, UserStatus

DRAFT = {
    "tomador": {"nome": "ABBa LTDA", "cnpj": "44555666000177"},
    "servico": {"descricao": "marcenaria", "codigo": "070201"},
    "valores": {"total": 1500.0, "aliquotaIss": 5.0},
}


def _ctx(prestador_id: int, conv_id: int, phone: str) -> ContextTomador:
    return ContextTomador(
        user=User(id=prestador_id, phone=phone, status=UserStatus.ACTIVE),
        text="", new_data=TomadorData(), db_data=TomadorData(),
        merged=TomadorData(), valid=TomadorData(), msg_type=MsgType.TEXT,
        conv_id=conv_id,
    )


def test_reconfirmar_apos_erro_reenfileira_a_mesma_nf(db):
    """Corrigir os dados e reconfirmar reusa a mesma linha em `nfs` (mesmo
    conv_id) — sem resetar status/tentativas, uma NF que caiu em ERROR ficaria
    presa lá para sempre, porque o worker só pega jobs QUEUED."""
    phone = "5521991112222"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")
    conv_id = db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "COLLECTING", "draft_json": "{}"},
        returning="id",
    )

    ctx = _ctx(prestador_id, conv_id, phone)
    nfs_id = TomadorManager(ctx).update_nf_from_draft(DRAFT)
    assert nfs_id is not None

    db.update("nfs", data={"status": "ERROR", "tentativas": 3, "erro_msg": "rejeitado"}, where={"id": nfs_id})

    same_id = TomadorManager(ctx).update_nf_from_draft(DRAFT)
    assert same_id == nfs_id

    nfs = db.select_one("nfs", where={"id": nfs_id})
    assert nfs["status"] == "QUEUED"
    assert nfs["tentativas"] == 0
    assert nfs["erro_msg"] is None
    assert nfs["aliquota_iss"] == 5.0
    assert nfs["codigo_servico"] == "070201"


def test_draft_sem_iss_resolvido_falha_explicitamente(db):
    """Sem cTribNac/alíquota no draft, a emissão não pode montar um payload
    coerente — falha alto em vez de cair no default silencioso de antes."""
    phone = "5521998887777"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")
    conv_id = db.insert(
        "conversations",
        data={"phone": phone, "prestador_id": prestador_id, "status": "COLLECTING", "draft_json": "{}"},
        returning="id",
    )
    ctx = _ctx(prestador_id, conv_id, phone)

    draft_sem_iss = {
        "tomador": {"nome": "ABBa LTDA", "cnpj": "44555666000177"},
        "servico": {"descricao": "marcenaria"},
        "valores": {"total": 1500.0},
    }
    with pytest.raises(InvalidTransactionError):
        TomadorManager(ctx).update_nf_from_draft(draft_sem_iss)
