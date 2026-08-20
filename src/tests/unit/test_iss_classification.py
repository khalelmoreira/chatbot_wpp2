from src.services.ai.ai_service import AIService
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import IssClassKey


def test_clear_description_resolves_to_known_code():
    fake_client = FakeAIClient(extract_json_responses=[{"value": "010601"}])
    ai = AIService(fake_client)

    codigo = ai.iss.classify(IssClassKey.SERVICE_CODE, "consultoria em tecnologia da informação")

    assert codigo == "010601"


def test_ambiguous_description_falls_back_to_unclassified():
    fake_client = FakeAIClient(extract_json_responses=[{"value": "UNCLASSIFIED"}])
    ai = AIService(fake_client)

    codigo = ai.iss.classify(IssClassKey.SERVICE_CODE, "sei lá, umas coisas")

    assert codigo == "UNCLASSIFIED"


def test_code_outside_known_list_is_treated_as_unclassified():
    """Defesa em profundidade: mesmo se o modelo devolver um código fora da lista
    conhecida, o parser rejeita e o AIClassifier cai no fallback — nunca confia
    cegamente no que a IA respondeu."""
    fake_client = FakeAIClient(extract_json_responses=[{"value": "999999"}])
    ai = AIService(fake_client)

    codigo = ai.iss.classify(IssClassKey.SERVICE_CODE, "algo bem específico")

    assert codigo == "UNCLASSIFIED"
