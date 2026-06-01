import json
from pathlib import Path
from src.services.webhook_wpp_service import processar_webhook
from src.flows.fluxo_principal import fluxo_principal

FIXTURES = Path("app/tests/integration/meta")

def load_fixtures(name):

    path = FIXTURES / name

    with open(path, encoding="utf-8") as f:
        return json.load(f)
    
def test_text_webhook():

    payload = load_fixtures("completo.json")

    processar_webhook(payload)