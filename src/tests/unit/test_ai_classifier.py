from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import AIClassifier, AIPrompt


def test_classifier_parses_valid_value():
    client = FakeAIClient(extract_json_responses=[{"value": "ONBOARDING"}])
    classifier = AIClassifier(
        client=client,
        prompt=AIPrompt(system="classifique"),
        schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        parser=lambda v: v,
        fallback="NENHUM",
    )

    assert classifier.classify("quero me cadastrar") == "ONBOARDING"


def test_classifier_returns_fallback_on_missing_key():
    client = FakeAIClient(extract_json_responses=[{}])
    classifier = AIClassifier(
        client=client,
        prompt=AIPrompt(system="classifique"),
        schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        parser=lambda v: v,
        fallback="NENHUM",
    )

    assert classifier.classify("oi") == "NENHUM"


def test_classifier_returns_fallback_when_parser_raises():
    client = FakeAIClient(extract_json_responses=[{"value": "algo_invalido"}])

    def parser(v):
        if v != "ONBOARDING":
            raise ValueError("valor fora do enum esperado")
        return v

    classifier = AIClassifier(
        client=client,
        prompt=AIPrompt(system="classifique"),
        schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        parser=parser,
        fallback="NENHUM",
    )

    assert classifier.classify("oi") == "NENHUM"
