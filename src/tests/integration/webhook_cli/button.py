from dispatcher import dispatch
from src.tests.generators.build_payload import build_button_reply_message

WEBHOOK_URL = "http://localhost:5000/webhook"

def main():
    print("\n=== WEBHOOK TEST CLI ===\n")
    print("1 - msg botao confirmar endereco")
    print("2 - msg botao confirmar tomador")
    print("3 - msg botao confirmar prestador")

    option = input("\nEscolha: ")

    payload = None

    if option == "1":
        print("\n1 = endereco_confirmado")
        print("2 = endereco_corrigir")
        escolha = input("\nEscolha: ")

        if escolha == "1":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="endereco_confirmado",
            )
        elif escolha == "2":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="endereco_corrigir",
            )

    elif option == "2":
        print("\n1 = tomador_confirmado")
        print("2 = tomador_corrigir")
        escolha = input("\nEscolha: ")

        if escolha == "1":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="tomador_confirmado",
            )
        elif escolha == "2":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="tomador_corrigir",
            )

    elif option == "3":
        print("\n1 = prestador_confirmado")
        print("2 = prestador_corrigir")
        escolha = input("\nEscolha: ")

        if escolha == "1":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="prestador_confirmado",
            )
        elif escolha == "2":
            payload = build_button_reply_message(
                phone="22666666666",
                button_id="prestador_corrigir",
            )

    if payload is None:
        print("Opção inválida")
        return

    dispatch(url=WEBHOOK_URL, payload=payload)


if __name__ == "__main__":
    main()