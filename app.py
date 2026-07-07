from flask import Flask, request, jsonify, render_template
import os
import logging
import atexit
from src.workers import EmissaoWorker, PollingWorker
from src.webhooks import WppWebhook, NotaasWebhook
from src.managers.tokens_manager import UploadTokensManager as TokensManager
from src.services.validators.security_service import verificar_ass
from src.database.tables_db import init_db
from src.services.notaas.ja_process import ja_process
from dotenv import load_dotenv

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

    payload_raw = request.get_data()
    assinatura = request.headers.get("X-Notaas-Signature")
    delivery_id = request.headers.get("X-Notaas-Delivery")
    
    print(f"PAYLOAD RAW: {payload_raw}\n")
    print(f"ASSINATURA: {assinatura}\n")

    if not assinatura:
        logger.warning("webhook notaas sem assinatura — secret configurado no dashboard?")
        return jsonify({"success": False, "error": "assinatura ausente"}), 401
    
    if not verificar_ass(payload_raw, assinatura):
        logger.warning("webhook notaas com assinatura inválida")
        return jsonify({"success": False, "error": "assinatura ausente"}), 401
    
    if not delivery_id:
        logger.warning("webhook notaas sem X-Notaas-Delivery — Notaas mudou o contrato?")
        return "OK", 200

    if ja_process(delivery_id):
        return "OK", 200
    
    payload = request.get_json()
    print(f"PAYLOAD RECEBIDO: {payload}\n")

    try:
        notaas = NotaasWebhook(payload)
        notaas.processar_webhook_notaas()
    except Exception as e:
        logger.exception(f"erro ao processar webhook notaas: {e}")
        return "ok", 200
    
    return "ok", 200

@app.route("/upload-certificado/<token>", methods=["GET"])
def form_upload(token: str):
    result = TokensManager().get_token(token)

    if not result or result["usado"] or expirado(result["expire_at"]):
        return render_template("token_invalido.html"), 410
    
    return render_template("upload_form.html", token=token)

@app.route("/upload-certificado/<token>", methods=["POST"])
def process_upload(token: str):

    result = TokensManager().update_usado(token)
    if not result:
        return jsonify({"error:": "token inválido, expirado ou já usado"}), 410
    
    prestador_id = result["prestador_id"]

    arquivo = request.files.get("certificado")
    senha = request.form.get("senha")

    if not arquivo or not senha:
        return jsonify({"error": "certificado e senha obrigatorios"}), 400
    
    certificado_bytes = arquivo.read()

    try:
        response = send_certificado_ntaas(prestador_id=prestador_id, certificado_bytes=certificado_bytes, senha=senha)

    finally:
        del certificado_bytes
        del senha

    return jsonify({"success": True})

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