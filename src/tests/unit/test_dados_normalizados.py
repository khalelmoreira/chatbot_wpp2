from src.services.ai_service import analisar_msg_nota_ai
from src.tests.generators.gen_msg_ai import gen_msg_fake
from src.services.validador_tomador import normalizar_dados_nf

qtd = 1
msg = gen_msg_fake(tipo="nfse", quantidade=qtd)
print(msg)
msg_ai = analisar_msg_nota_ai(msg)
print(msg_ai)
dados_normalizados = normalizar_dados_nf(msg_ai)
print(dados_normalizados)