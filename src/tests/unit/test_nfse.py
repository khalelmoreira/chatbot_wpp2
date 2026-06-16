from chatbot_wpp2.src.services.shared.ai_service import analisar_msg_nota_ai
from chatbot_wpp2.src.services.shared.emission_service import emitir_nf

mensagem = """
emitir nota para empresa ACME LTDA
cnpj 12.345.678/0001-99
email financeiro@acme.com
serviço de manutenção
valor 150 reais
aliquota 2%
codigo 010700
"""

dados_nota = analisar_msg_nota_ai(mensagem)

nota = emitir_nf(dados_nota)

print(nota)