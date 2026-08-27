import os

from flask import Blueprint, request

from src.handlers.telegram_handler import telegram_handler

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != os.getenv("TELEGRAM_WEBHOOK_SECRET"):
        return "Token invalido", 403

    data = request.get_json()
    if not data:
        return "ok", 200

    telegram_handler(data)
    return "ok", 200
