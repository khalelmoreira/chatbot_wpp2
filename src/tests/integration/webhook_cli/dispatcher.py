import json
import requests

def dispatch(url: str, payload: dict) -> None:

    print("\n=== REQUEST ===\n")

    print(json.dumps(
        payload,
        indent=2,
        ensure_ascii=False
    ))

    response = requests.post(
        url,
        json=payload
    )

    print("\n=== RESPONSE ===\n")

    print(f"Status: {response.status_code}")

    try:
        print(json.dumps(
            response.json(),
            indent=2,
            ensure_ascii=False
        ))

    except Exception:
        print(response.text)