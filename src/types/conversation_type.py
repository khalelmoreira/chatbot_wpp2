from dataclasses import dataclass
from typing import Protocol

# ─── Contrato da IA ──────────────────────────────────────────────────────────
# StateMachine não sabe como a IA funciona — só o que ela precisa receber e retornar

@dataclass
class AIResponse:
    message: str                   # texto para o usuário
    extraido: dict                 # dados novos identificados nesta mensagem
    intencao: bool = False         # intenção de emissao, ia detecta

class AIClient(Protocol):
    def process(self, history: list[dict], draft: dict, state: str) -> AIResponse:...