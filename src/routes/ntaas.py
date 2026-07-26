import logging
from flask import Blueprint, request, jsonify, render_template
from src.services.validators.security_service import validate_assinature
from src.services.ntaas.ja_process import ja_process

logger = logging.getLogger(__name__)
ntaas_bp = Blueprint("ntaas", __name__)

def _validate_webhook_ntaas(payload_raw: bytes, signature: str | None, delivery_id: str | None):
    if not signature:
        return "assinatura ausente", 401
    if not validate_assinature(payload_raw, signature):
        return "assinatura inválida", 401
    if not delivery_id:
        return None, 200
    return None, None

@ntaas_bp.route("/webhook/notaas", methods=["POST", "GET"], strict_slashes=False)
def ntaas_webhook():

    payload_raw = request.get_data()
    signature = request.headers.get("X-Notaas-Signature")
    delivery_id = request.headers.get("X-Notaas-Delivery")
    
    print(f"PAYLOAD RAW: {payload_raw}\n")
    print(f"ASSINATURA: {signature}\n")

    erro, status = _validate_webhook_ntaas(payload_raw, signature, delivery_id)

    if erro:
        logger.warning(f"webhook notaas rejeitado: {erro}")
        return jsonify({"success": False, "error": erro}), status
    if status == 200:
        return "OK", 200

    if ja_process(delivery_id):
        return "OK", 200
    
    payload = request.get_json()
    print(f"PAYLOAD RECEBIDO: {payload}\n")

    try:
        NotaasWebhook(payload).processar_webhook_notaas()
    except Exception as e:
        logger.exception(f"erro ao processar webhook notaas: {e}")
        return "ok", 200
    
    return "ok", 200

@ntaas_bp.route("/upload-certificate/<token>", methods=["GET"])
def form_upload(token: str):
    result = TokensManager().get_token(token)

    if not result or result["used"] or expirado(result["expire_at"]):
        return render_template("token_invalido.html"), 410
    
    return render_template("upload_form.html", token=token)

@ntaas_bp.route("/upload-certificate/<token>", methods=["POST"])
def process_upload(token: str):

    row = TokensManager().get_token(token)
    if not row or row["used"] or expirado(row["expire_at"]):
        return jsonify({"error:": "token inválido, expirado ou já usado"}), 410
    
    prestador_id = row["prestador_id"]
    
    prestador = PrestadorManager().get_project_id(prestador_id)
    if not prestador:
        return jsonify({"error": "prestador não está na etapa de certificado"}), 409
    
    arquivo = request.files.get("certificado")
    senha = request.form.get("senha")

    if not arquivo or not senha:
        return jsonify({"error": "certificado e senha obrigatorios"}), 400
    
    certificado_bytes = arquivo.read()

    try:
        CertificateService().send_e_persist_certificate()

    except NtaasCertificadoError as e:
        return jsonify({"error": str(e)}), 400
    
    finally:
        del certificado_bytes
        del senha

    TokensManager().update_used(token)
    return jsonify({"success": True})