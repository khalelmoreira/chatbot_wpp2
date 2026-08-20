import pytest

from src.managers.iss.iss_rate_manager import IssRateManager
from src.services.ai.ai_service import AIService
from src.services.iss.iss_resolution_service import IssResolutionService
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import IssRate, IssResolutionError

RJ = "3304557"


def _service(responses: list[dict]) -> IssResolutionService:
    ai = AIService(FakeAIClient(extract_json_responses=responses))
    return IssResolutionService(ai=ai, rates=IssRateManager())


def test_clear_description_resolves_to_code_and_rate(db):
    IssRateManager().upsert_rates([IssRate(RJ, "010601", 3.0, "2026-01-01", None)])
    service = _service([{"value": "010601"}])

    result = service.resolve("consultoria em tecnologia da informação", RJ)

    assert not result.unclassified
    assert result.codigo_tributacao_nacional == "010601"
    assert result.aliquota == 3.0


def test_ambiguous_description_returns_explicit_unclassified(db):
    service = _service([{"value": "UNCLASSIFIED"}])

    result = service.resolve("sei lá, algo aleatório", RJ)

    assert result.unclassified
    assert result.codigo_tributacao_nacional is None
    assert result.aliquota is None


def test_valid_code_with_no_current_rate_row_fails_visibly(db):
    """Código real, mas sem linha vigente na tabela local (não sincronizada ainda,
    ou vigência expirada) — deve levantar, nunca devolver aliquota=0/None em silêncio."""
    service = _service([{"value": "010601"}])

    with pytest.raises(IssResolutionError):
        service.resolve("consultoria em tecnologia da informação", RJ)
