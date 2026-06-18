from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.database.tables_db import init_db
from src.webhooks.wpp_webhook import wpp_webhook
from src.workers.worker_service import start_workers
from src.webhooks.notaas_webhook import notaas_webhook
from src.services.shared.security_service import verificar_ass

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
        
        wpp_webhook(data)

        return "ok", 200

@app.route("/webhook/notaas", methods=["POST", "GET"], strict_slashes=False)
def webhook_notaas():

    payload_raw = request.get_data()
    print(f"PAYLOAD RAW: {payload_raw}\n")

    assinatura = request.headers.get("X-Notaas-Signature")
    print(f"ASSINATURA: {assinatura}\n")

    if not assinatura:
        return jsonify({
            "success": False,
            "error": "assinatura ausente"
        }), 401
    
    if not verificar_ass(payload_raw, assinatura):
        return jsonify({
            "success": False,
            "error": "assinatura ausente"
        }), 401
    
    payload = request.get_json()
    print(f"PAYLOAD: {payload}\n")

    resultado = notaas_webhook(payload)

    return jsonify(resultado), 200

if __name__ == "__main__":
    init_db()
    start_workers()
    app.run(debug=True, use_reloader=False, port=5000)