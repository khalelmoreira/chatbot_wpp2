from flask import Flask, request
import os
import logging
import atexit
from src.workers import EmissaoWorker, PollingWorker
from src.webhooks import WppWebhook, NotaasWebhook
from src.services.shared.security_service import verificar_ass
from dotenv import load_dotenv
from src.database.tables_db import init_db

load_dotenv()
logger = logging.getLogger(__name__)
emissao_worker = EmissaoWorker(intervalo_poll=2.0)
polling_worker = PollingWorker(intervalo_poll=20.0)
app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == os.getenv("VERIFY_TOKEN"):
            return challenge
        return "Token invalido", 403
    

    if request.method == "POST":

        data = request.get_json()
        if not data:
            return "ok", 200
        
        wpp = WppWebhook(data)
        wpp.wpp_webhook()
        return "ok", 200

@app.route("/webhook/notaas", methods=["POST", "GET"], strict_slashes=False)
def webhook_notaas():

    # payload_raw = request.get_data()
    # print(f"PAYLOAD RAW: {payload_raw}\n")

    # assinatura = request.headers.get("X-Notaas-Signature")
    # print(f"ASSINATURA: {assinatura}\n")

    # if not assinatura:
    #     return jsonify({
    #         "success": False,
    #         "error": "assinatura ausente"
    #     }), 401
    
    # if not verificar_ass(payload_raw, assinatura):
    #     return jsonify({
    #         "success": False,
    #         "error": "assinatura ausente"
    #     }), 401
    
    payload = request.get_json()
    print(f"PAYLOAD RECEBIDO: {payload}\n")

    try:
        notaas = NotaasWebhook(payload)
        notaas.processar_webhook_notaas()
    except Exception as e:
        logger.exception("erro ao processar webhook notaas")
        return "ok", 200
    
    return "ok", 200

def _shutdown():
    logger.info("sinal de shutdown recebido")
    emissao_worker.stop()
    polling_worker.stop()

atexit.register(_shutdown)

if __name__ == "__main__":
    init_db()
    emissao_worker.start()
    polling_worker.start()
    app.run(debug=True, use_reloader=False, port=5000)