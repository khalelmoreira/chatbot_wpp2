dados = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1454008646386065",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "16505551111",
              "phone_number_id": "123456123"
            },
            "contacts": [
              {
                "profile": {
                  "name": "test user name"
                },
                "wa_id": "16315551181",
                "user_id": "US.13491208655302741918"
              }
            ],
            "messages": [
              {
                "id": "ABGGFlA5Fpa",
                "timestamp": "1504902988",
                "from": "16315551181",
                "from_user_id": "US.13491208655302741918",
                "type": "text",
                "text": {
                  "body": "this is a text message"
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
entry = dados["entry"][0]
changes = entry["changes"][0]
value = changes["value"]
messages = value["messages"]

print(f"\n\n{entry}\n")
print(f"\n\n{changes}\n")
print(f"\n\n{value}\n")
print(f"\n\n{messages}\n")