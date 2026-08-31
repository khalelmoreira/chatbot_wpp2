"""Black-box tomador (NFS-e emission) scenario: real /webhook POSTs, no direct flow calls.
Prestador account creation/CNPJ/certificate are prestador-side concerns (see
test_prestador_signup_scenario.py) — this scenario starts from an already-ACTIVE prestador,
since that's the only precondition ConvStatus flows care about.
"""
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.types import BotaoId

PHONE = "5511900001111"
ISS_CODE = "010601"  # "Consultoria e assessoria em informática" — src/models/national_service_codes.py


def _ativa_prestador(db, phone: str) -> int:
    return db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")


def _seed_iss_rate(db) -> None:
    db.insert(
        "iss_rates",
        data={
            "codigo_municipio": RJ_CODIGO_MUNICIPIO,
            "codigo_tributacao_nacional": ISS_CODE,
            "aliquota": 0.02,
            "vigencia_inicio": "2020-01-01",
        },
    )


def test_tomador_completes_emission_from_collecting_to_queued(scenario, db):
    _ativa_prestador(db, PHONE)
    _seed_iss_rate(db)

    scenario.queue_ai(
        {"value": "EMITIR"},
        {
            "tomador": {"nome": "Cliente LTDA", "cnpj": "11222333000181"},
            "servico": {"descricao": "Consultoria"},
            "valores": {"total": 1500},
        },
        {"value": ISS_CODE},
    )
    resp = scenario.send_text(PHONE, "quero emitir nota para Cliente LTDA cnpj 11222333000181 consultoria 1500")
    assert resp.status_code == 200

    conv = db.select_one("conversations", where={"phone": PHONE})
    assert conv["status"] == "CONFIRMING"

    resp = scenario.send_button(PHONE, BotaoId.TOMADOR_CONFIRMADO)
    assert resp.status_code == 200

    conv = db.select_one("conversations", where={"id": conv["id"]})
    assert conv["status"] == "QUEUED"

    nf = db.select_one("nfs", where={"conv_id": conv["id"]})
    assert nf is not None
    assert nf["codigo_servico"] == ISS_CODE
    assert nf["aliquota_iss"] == 0.02


def test_tomador_incomplete_data_stays_in_collecting_and_asks_for_more(scenario, db):
    _ativa_prestador(db, PHONE)

    scenario.queue_ai(
        {"value": "EMITIR"},
        {"tomador": {"nome": "Cliente LTDA"}},
    )
    scenario.send_text(PHONE, "quero emitir nota para Cliente LTDA")

    conv = db.select_one("conversations", where={"phone": PHONE})
    assert conv["status"] == "COLLECTING"
