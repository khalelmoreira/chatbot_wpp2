import pytest

from src.managers.user_manager import PrestadorManager
from src.types import (
    ContextPrestador,
    InvalidTransactionError,
    MsgType,
    PrestadorData,
    User,
    UserStatus,
)


def _ctx(prestador_id: int, status: UserStatus, valid: PrestadorData) -> ContextPrestador:
    return ContextPrestador(
        user=User(id=prestador_id, phone="5511999999999", status=status),
        text="", new_data=PrestadorData(), db_data=PrestadorData(),
        merged=PrestadorData(), valid=valid, msg_type=MsgType.TEXT,
    )


def _novo_prestador(db, status: str) -> int:
    return db.insert("prestador", data={"phone": "5511999999999", "status": status}, returning="id")


def test_update_valid_so_aplica_em_collecting(db):
    prestador_id = _novo_prestador(db, "COLLECTING")
    ctx = _ctx(prestador_id, UserStatus.COLLECTING, PrestadorData(razao_social="Empresa LTDA"))

    PrestadorManager(ctx).update_valid()

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["razao_social"] == "Empresa LTDA"


def test_update_valid_recusa_fora_de_collecting(db):
    prestador_id = _novo_prestador(db, "CONFIRMING")
    ctx = _ctx(prestador_id, UserStatus.CONFIRMING, PrestadorData(razao_social="Empresa LTDA"))

    with pytest.raises(InvalidTransactionError):
        PrestadorManager(ctx).update_valid()


def test_update_project_id_so_aplica_em_project(db):
    prestador_id = _novo_prestador(db, "PROJECT")
    ctx = _ctx(prestador_id, UserStatus.PROJECT, PrestadorData())

    PrestadorManager(ctx).update_project_id("proj_123", UserStatus.CERTIFICATE)

    row = db.select_one("prestador", where={"id": prestador_id})
    assert row["status"] == "CERTIFICATE"
    assert row["ntaas_project_id"] == "proj_123"


def test_update_project_id_recusa_fora_de_project(db):
    prestador_id = _novo_prestador(db, "CONFIRMING")
    ctx = _ctx(prestador_id, UserStatus.CONFIRMING, PrestadorData())

    with pytest.raises(InvalidTransactionError):
        PrestadorManager(ctx).update_project_id("proj_123", UserStatus.CERTIFICATE)
