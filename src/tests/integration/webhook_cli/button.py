from dispatcher import dispatch
from src.tests.generators.build_payload import build_button_reply_message

WEBHOOK_URL = "http://localhost:5000/webhook"

def main():

    print("\n=== WEBHOOK TEST CLI ===\n")

    print("1 - Mensagem interactive button")
    print("2 - Status entregue")

    option = input("\nEscolha: ")

    if option == "1":

        phone = input("Telefone: ")

        print("1 = endereco_confirmado")
        print("2 = endereco_corrigir")

        escolha = input("\nEscolha: ")

        if escolha == "1":

            payload = build_button_reply_message(
            phone=phone,
            button_id="endereco_confirmado"
        )
        
        if escolha == "2":

            payload = build_button_reply_message(
            phone=phone,
            button_id="endereco_corrigido"
        )

    else:
        print("Opção inválida")
        return

    dispatch(
        url=WEBHOOK_URL,
        payload=payload
    )


if __name__ == "__main__":
    main()