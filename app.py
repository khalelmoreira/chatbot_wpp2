from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.database.tables_db import init_db
from src.services.webhook_wpp_service import processar_webhook
from src.services.notaas_service import processar_webhook_notaas, verificar_assinatura

load_dotenv()

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    #Verificacao da Meta
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == os.getenv("VERIFY_TOKEN"):
            return challenge
        return "Token invalido", 403
    

    if request.method == "POST":

        print(f"\nentrou post\n")
        #Separa dados do json
        data = request.get_json()
        print(f"recebeu json: {data}\n")
        if not data:
            return "ok", 200
        
        processar_webhook(data)

        return "ok", 200

@app.route("/webhook/notaas", methods=["POST"])
def webhook_notaas():

    payload_raw = request.get_data()

    assinatura = request.headers.get("X-Notaas-Signature")

    if not assinatura:
        return jsonify({
            "success": False,
            "error": "assinatura ausente"
        }), 401
    
    if not verificar_assinatura(payload_raw, assinatura):
        return jsonify({
            "success": False,
            "error": "assinatura ausente"
        }), 401
    
    payload = request.get_json()

    resultado = processar_webhook_notaas(payload)

    return jsonify(resultado), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)