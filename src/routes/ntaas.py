from flask import Blueprint, request, jsonify, render_template
from src.handlers.ntaas_handler import ntaas_handler
from src.handlers.certificate_handler import certificate_form_handler, certificate_upload_handler

ntaas_bp = Blueprint("ntaas", __name__)

@ntaas_bp.route("/webhook/notaas", methods=["POST", "GET"], strict_slashes=False)
def ntaas_webhook():

    payload_raw: bytes = request.get_data()
    signature = request.headers.get("X-Notaas-Signature")
    delivery_id = request.headers.get("X-Notaas-Delivery")

    result = ntaas_handler(payload_raw, signature, delivery_id)
    return jsonify(result.body), result.status

@ntaas_bp.route("/upload-certificate/<token>", methods=["GET"])
def form_upload(token: str):

    result = certificate_form_handler(token)
    if not result.ok:
        return render_template("token_invalido.html"), result.status
    return render_template("upload_form.html", token=token)

@ntaas_bp.route("/upload-certificate/<token>", methods=["POST"])
def process_upload(token: str):

    arq = request.files.get("certificado")
    pasw = request.form.get("pasw")

    result = certificate_upload_handler(token, arq, pasw)
    return jsonify(result.body), result.status