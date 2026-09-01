from src.services.ai.ai_client import _with_history
from src.services.ai.history import to_ai_history
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.types import AIClassifier, AIPrompt


def _rows(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    return [{"role": r, "content": c} for r, c in pairs]


def test_to_ai_history_maps_roles_and_lowercases():
    out = to_ai_history(_rows(("USER", "oi"), ("AI", "olá"), ("USER", "sim")))
    assert out == [
        {"role": "user", "content": "oi"},
        {"role": "ai", "content": "olá"},
        {"role": "user", "content": "sim"},
    ]


def test_to_ai_history_drops_leading_ai_turns_and_empty_content():
    out = to_ai_history(_rows(("AI", "saudação"), ("AI", "  "), ("USER", "oi"), ("AI", "resposta")))
    assert out == [
        {"role": "user", "content": "oi"},
        {"role": "ai", "content": "resposta"},
    ]


def test_with_history_renames_ai_to_assistant_and_appends_current():
    msgs = _with_history([{"role": "user", "content": "oi"}, {"role": "ai", "content": "olá"}], "sim")
    assert msgs == [
        {"role": "user", "content": "oi"},
        {"role": "assistant", "content": "olá"},
        {"role": "user", "content": "sim"},
    ]


def test_with_history_none_is_just_the_current_message():
    assert _with_history(None, "sim") == [{"role": "user", "content": "sim"}]


def test_classifier_forwards_history_to_client():
    client = FakeAIClient(extract_json_responses=[{"value": "ONBOARDING"}])
    classifier = AIClassifier(
        client=client,
        prompt=AIPrompt(system="classifique"),
        schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        parser=lambda v: v,
        fallback="NENHUM",
    )
    history = [{"role": "ai", "content": "quer começar seu cadastro?"}]

    assert classifier.classify("sim", history) == "ONBOARDING"
    assert client.last_history == history
