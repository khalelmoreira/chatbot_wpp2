from src.tests.generators.base import (
    generate_message_id,
    generate_timestamp
)

def build_text_message(phone: str, text: str) -> dict:

    return {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "145678901234567",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "59792598778978",
              "phone_number_id": "123456789012345"
            },
            "contacts": [
              {
                "profile": {
                  "name": "João Silva"
                },
                "wa_id": "4354276655487995478",
                "identity_key_hash": "e4f7c2d1a9b8c6f5"
              }
            ],
            "messages": [
              {
                "from": phone,
                "id": generate_message_id(),
                "timestamp": generate_timestamp(),
                "type": "text",
                "text": {
                  "body": text
                },
                "context": {
                  "forwarded": "true",
                  "frequently_forwarded": "false"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}