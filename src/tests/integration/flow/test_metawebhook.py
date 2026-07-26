import json
from pathlib import Path
from chatbot_wpp2.src.handlers.wpp_handler import processar_webhook
from chatbot_wpp2.src.handlers.initial_handler import fluxo_principal

FIXTURES = Path("app/tests/integration/meta")

def load_fixtures(name):

    path = FIXTURES / name

    with open(path, encoding="utf-8") as f:
        return json.load(f)
    
def test_text_webhook():

    payload = load_fixtures("completo.json")

    processar_webhook(payload)