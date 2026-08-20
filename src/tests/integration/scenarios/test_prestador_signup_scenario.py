"""Black-box prestador onboarding scenario, driven end-to-end through the real /webhook route.

Scoped to COLLECTING -> ADDRESS -> CONFIRMING -> PROJECT -> CERTIFICATE. It stops short of
ACTIVE deliberately: the last step (ACTIVE) only happens after a real certificate file is
POSTed to /upload-certificate, which is an HTTP upload, not a chat message, and is already
covered by test_routes.py. Faking a .pfx upload here would just re-test that route with extra
steps, not add scenario coverage.

Three real external integrations sit on this path and are faked the same way ai_client_factory
is faked in conftest.py: Receita Federal (get_cnpj_info), ViaCEP (get_endereco_by_cep), and the
Notaas project-creation call (ProjectService.create_project).
"""
from src.services.sign_up import collecting_user_service
from src.services.sign_up.project_service import ProjectService
from src.types import Address, BotaoId

PHONE = "5511900002222"


def test_prestador_onboards_from_collecting_to_certificate(scenario, db, monkeypatch):
    monkeypatch.setattr(
        collecting_user_service, "get_cnpj_info",
        lambda cnpj: {"descricao_situacao_cadastral": "ATIVA"},
    )
    monkeypatch.setattr(
        collecting_user_service, "get_endereco_by_cep",
        lambda cep: Address(logradouro="Rua Teste", bairro="Centro", cidade="São Paulo", uf="SP"),
    )
    monkeypatch.setattr(ProjectService, "create_project", lambda self, org_token: "fake-project-id")
    monkeypatch.setenv("NTAAS_ORG_TOKEN", "fake-org-token")
    monkeypatch.setenv("APP_DOMAIN", "https://example.test")

    # Turn 1: new phone, full CNPJ/company data in one message -> intent classify + data extract.
    scenario.queue_ai(
        {"value": "ONBOARDING"},
        {
            "razao_social": "Empresa Teste LTDA",
            "cnpj": "11222333000181",
            "email": "empresa@teste.com",
            "regime_tributario": "3",
            "cep": "01310100",
        },
    )
    resp = scenario.send_text(
        PHONE,
        "Quero emitir notas. Empresa Teste LTDA, cnpj 11222333000181, "
        "email empresa@teste.com, regime simples, cep 01310100",
    )
    assert resp.status_code == 200

    prestador = db.select_one("prestador", where={"phone": PHONE})
    assert prestador["status"] == "ADDRESS"

    # Turn 2: street number completes the address -> CONFIRMING.
    scenario.queue_ai({"numero": "123"})
    scenario.send_text(PHONE, "numero 123")

    prestador = db.select_one("prestador", where={"id": prestador["id"]})
    assert prestador["status"] == "CONFIRMING"

    # Turn 3: confirm button -> PROJECT (Notaas project created) -> CERTIFICATE (link sent).
    resp = scenario.send_button(PHONE, BotaoId.PRESTADOR_CONFIRMADO)
    assert resp.status_code == 200

    prestador = db.select_one("prestador", where={"id": prestador["id"]})
    assert prestador["status"] == "CERTIFICATE"


def test_prestador_with_inactive_cnpj_is_rejected_before_address(scenario, db, monkeypatch):
    monkeypatch.setattr(
        collecting_user_service, "get_cnpj_info",
        lambda cnpj: {"descricao_situacao_cadastral": "BAIXADA"},
    )

    scenario.queue_ai(
        {"value": "ONBOARDING"},
        {
            "razao_social": "Empresa Baixada LTDA",
            "cnpj": "11222333000181",
            "email": "baixada@teste.com",
            "regime_tributario": "3",
            "cep": "01310100",
        },
    )
    scenario.send_text(
        PHONE,
        "Empresa Baixada LTDA, cnpj 11222333000181, email baixada@teste.com, regime simples, cep 01310100",
    )

    prestador = db.select_one("prestador", where={"phone": PHONE})
    assert prestador["status"] == "COLLECTING"
