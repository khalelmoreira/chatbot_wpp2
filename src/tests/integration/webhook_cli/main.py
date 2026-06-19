from dispatcher import dispatch
from src.tests.generators.build_payload import build_text_message

WEBHOOK_URL = "http://localhost:5000/webhook"

def main():

    print("\n=== WEBHOOK TEST CLI ===\n")

    print("1 - Mensagem de texto")
    print("2 - Status entregue")

    option = input("\nEscolha: ")

    if option == "1":

        text = input("Mensagem: ")

        payload = build_text_message(
            phone="22666666666",
            text=text
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