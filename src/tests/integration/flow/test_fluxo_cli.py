from src.flows.fluxo_ativo import fluxo_ativo
from src.repositories.db import init_db

def test_fluxo_cli():

    init_db()

    phone = "22999999999"

    user = {
        "estado": "ativo"
    }

    print("\n=== TESTE CLI FLUXO ATIVO ===\n")
    print("Digite mensagens como se fossem do WhatsApp.")
    print("Digite 'q' para encerrar.\n")

    while True:

        try:
            user_text = input("Cliente: ")

            if user_text.lower() in ["q", "exit", "quit"]:
                print("\nEncerrando teste.\n")
                break

            if not user_text.strip():
                continue

            print("\n--- PROCESSANDO ---\n")

            response = fluxo_ativo(
                phone=phone,
                user_text=user_text,
                user=user
            )

            print(f"\nResposta fluxo: {response}\n")
            print("-------------------\n")

        except KeyboardInterrupt:
            print("\n\nTeste interrompido.\n")
            break

        except Exception as e:
            print(f"\nERRO: {e}\n")

if __name__ == "__main__":
    test_fluxo_cli()