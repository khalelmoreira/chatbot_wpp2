from src.services.ai_service import analisar_msg_nota_ai
import json

mensagem = """
emitir nota para empresa ACME LTDA
cnpj 12.345.678/0001-99
email financeiro@acme.com
serviço de manutenção
valor 150 reais
aliquota 2%
codigo 0107
"""

TESTES = [

    "nota para joao cpf 12345678900 valor 150",

    "emitir nf para acme cnpj 12.345.678/0001-99 email financeiro@acme.com",

    "faz uma nota de 250 referente consultoria",

    "empresa XPTO valor 1200 aliquota 5% codigo 1401",

    "cliente maria email maria@gmail.com"
]

# for msg in TESTES:

#     print("=" * 50)
#     print(msg)

#     resultado = analisar_msg_nota_ai(msg)

#     print(json.dumps(resultado, indent=2, ensure_ascii=False))


def test_extracao_basica():

    texto = """
    emitir nota para ACME LTDA
    cnpj 12.345.678/0001-99
    valor 150 reais
    """

    resultado = analisar_msg_nota_ai(texto)

    assert resultado["tomador"]["cnpj"] == "12345678000199"
    assert resultado["valores"]["total"] == 150


while True:

    texto = input("\nMensagem: ")

    if texto == "sair":
        break

    resultado = analisar_msg_nota_ai(texto)

    print(json.dumps(resultado, indent=2, ensure_ascii=False))

