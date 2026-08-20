from src.services.errors.error_notifier import (
    MSG_GENERICA,
    MSG_IA_INDISPONIVEL,
    MSG_NOTAAS_INDISPONIVEL,
    mensagem_para_erro,
    notificar_erro_processamento,
)
from src.types import AIClientRetryableError, DadosInvalidosError


def test_erro_de_ia_vira_mensagem_especifica():
    assert mensagem_para_erro(AIClientRetryableError("timeout")) == MSG_IA_INDISPONIVEL


def test_erro_da_notaas_vira_mensagem_especifica():
    assert mensagem_para_erro(DadosInvalidosError("cnpj invalido")) == MSG_NOTAAS_INDISPONIVEL


def test_erro_desconhecido_vira_mensagem_generica():
    assert mensagem_para_erro(ValueError("algo qualquer")) == MSG_GENERICA


def test_notificar_erro_processamento_salva_mensagem_para_usuario(db):
    phone = "5521991112222"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")

    notificar_erro_processamento(prestador_id, phone, AIClientRetryableError("timeout"))

    msgs = db.select("messages", where={"prestador_id": prestador_id})
    assert any(m["content"] == MSG_IA_INDISPONIVEL for m in msgs)


def test_notificar_erro_processamento_sem_prestador_nao_levanta(db):
    notificar_erro_processamento(None, "5521999999999", ValueError("x"))
