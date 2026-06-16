from chatbot_wpp2.src.services.shared.ai_service import analisar_msg_nota_ai
from src.tests.generators.gen_msg_ai import gen_msg_fake


qtd = 1
msg = gen_msg_fake(tipo="nfse", quantidade=qtd)
print(msg)
msg_ai = analisar_msg_nota_ai(msg)
print(msg_ai)