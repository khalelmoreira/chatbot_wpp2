from dispatcher import dispatch
from src.tests.generators.build_payload import build_button_reply_message

WEBHOOK_URL = "http://localhost:5000/webhook"

def main():

    print("\n=== WEBHOOK TEST CLI ===\n")

    print("1 - msg botao confirmar endereco")
    print("2 - msg botao confimar tomador")

    option = input("\nEscolha: ")

    if option == "1":

        phone = input("Telefone: ")

        print("\n1 = endereco_confirmado")
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
            
    if option == "2":

        phone = input("Telefone: ")

        print("\n1 = tomador_confirmado")
        print("2 = tomador_corrigir")

        escolha = input("\nEscolha: ")

        if escolha == "1":

            payload = build_button_reply_message(
            phone=phone,
            button_id="tomador_confirmado"
        )
        
        if escolha == "2":

            payload = build_button_reply_message(
            phone=phone,
            button_id="tomador_corrigir"
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