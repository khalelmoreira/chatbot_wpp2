from src.types import AIClient


class FakeAIClient(AIClient):
    """Test double para AIClient — sem rede, sem chaves. `extract_json_responses` é consumida
    em ordem, uma resposta por chamada; `extract_text_response` é fixa."""

    def __init__(self, extract_json_responses: list[dict] | None = None, extract_text_response: str = ""):
        self._extract_json_responses = list(extract_json_responses or [])
        self._extract_text_response = extract_text_response
        self.extract_calls: list[str] = []
        self.text_calls: list[str] = []
        self.last_history: list[dict[str, str]] | None = None
        self.histories: list[list[dict[str, str]] | None] = []

    def extract_json(
        self, system_prompt: str, user_msg: str, schema: dict,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        self.extract_calls.append(user_msg)
        self.last_history = history
        self.histories.append(history)
        if not self._extract_json_responses:
            return {}
        return self._extract_json_responses.pop(0)

    def queue_json(self, *responses: dict) -> None:
        """Appends responses to be consumed in order by later extract_json/classify calls.
        Used by black-box scenarios that drive several AI-backed steps in one turn."""
        self._extract_json_responses.extend(responses)

    def extract_text(
        self, system_prompt: str, user_msg: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        self.text_calls.append(user_msg)
        self.last_history = history
        self.histories.append(history)
        return self._extract_text_response
