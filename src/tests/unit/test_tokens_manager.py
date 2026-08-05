from datetime import datetime, timedelta, timezone
from src.managers.tokens_manager import TokensManager
from src.services.ntaas.upload_certificate import expirado


def test_token_nao_pode_ser_usado_duas_vezes(db):
    prestador_id = db.insert("prestador", data={"phone": "5511999999999", "status": "CERTIFICATE"}, returning="id")

    tokens = TokensManager()
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    tokens.insert_token("tok_abc", prestador_id=prestador_id, project_id="proj_123", expire_at=expire_at)

    primeira = tokens.update_used("tok_abc")
    segunda = tokens.update_used("tok_abc")

    assert primeira is not None
    assert segunda is None


def test_token_expirado_e_detectado():
    passado = datetime.now(timezone.utc) - timedelta(minutes=1)
    futuro = datetime.now(timezone.utc) + timedelta(minutes=1)

    assert expirado(passado) is True
    assert expirado(futuro) is False


def test_get_token_inexistente_retorna_none(db):
    assert TokensManager().get_token("token_que_nao_existe") is None
