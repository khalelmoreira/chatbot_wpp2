from flask import Blueprint, request
import os
from src.handlers.wpp_handler import wpp_handler

wpp_bp = Blueprint("wpp", __name__)

@wpp_bp.route("/webhook", methods=["GET", "POST"])
def wpp_webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == os.getenv("VERIFY_TOKEN") and challenge is not None:
            return challenge
        return "Token invalido", 403

    data = request.get_json()
    if not data:
        return "ok", 200

    wpp_handler(data)
    return "ok", 200