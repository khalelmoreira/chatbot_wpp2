"""Fully automated, no-terminal black-box scenarios: drive the real /webhook route
(Flask test client, in-process, no live server) through several conversational turns
and assert on resulting DB state. Two things a raw HTTP call can't get past on its own:

- TEXT messages are buffered for DEBOUNCE_SECONDS before processing (see
  src/services/wpp/debounce_service.py). We patch that to flush synchronously so a
  scripted turn resolves immediately instead of sleeping seconds per message.
- The AI layer is a real network call. We patch ai_client_factory.build_ai_client to
  return one shared FakeAIClient per test, and scenarios queue its responses in the
  exact order the flow under test will consume them.
"""
import pytest
from flask import Flask

from src.handlers import wpp_handler as wpp_handler_module
from src.routes.wpp import wpp_bp
from src.services.ai import ai_client_factory
from src.tests.fixtures.fake_ai_client import FakeAIClient
from src.tests.generators.build_payload import build_button_reply_message, build_text_message


class Scenario:
    """Thin wrapper around the Flask test client + shared FakeAIClient for one scenario."""

    def __init__(self, client, ai: FakeAIClient):
        self.client = client
        self.ai = ai

    def queue_ai(self, *responses: dict) -> None:
        self.ai.queue_json(*responses)

    def send_text(self, phone: str, text: str):
        return self.client.post("/webhook", json=build_text_message(phone=phone, text=text))

    def send_button(self, phone: str, button_id: str):
        return self.client.post("/webhook", json=build_button_reply_message(phone=phone, button_id=button_id))


@pytest.fixture
def scenario(db, monkeypatch) -> Scenario:
    monkeypatch.setattr(wpp_handler_module, "buffer_message", lambda msg, on_flush: on_flush(msg))

    ai_client = FakeAIClient()
    monkeypatch.setattr(ai_client_factory, "build_ai_client", lambda: ai_client)

    app = Flask("scenario_app")
    app.register_blueprint(wpp_bp)
    app.testing = True

    return Scenario(app.test_client(), ai_client)
