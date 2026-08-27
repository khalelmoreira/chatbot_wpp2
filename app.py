import atexit
import logging

from dotenv import load_dotenv
from flask import Flask

from src.database.tables_db import init_db
from src.logging_config import setup_logging
from src.routes import ntaas_bp, telegram_bp, wpp_bp
from src.workers import EmissaoWorker

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)
emissao_worker = EmissaoWorker(intervalo_poll=2.0)

def create_app() -> Flask:
    app = Flask(__name__, template_folder="src/models")
    app.register_blueprint(wpp_bp)
    app.register_blueprint(ntaas_bp)
    app.register_blueprint(telegram_bp)
    return app

def _shutdown():
    logger.info("sinal de shutdown recebido")
    emissao_worker.stop()

init_db()
app = create_app()

if __name__ == "__main__":
    emissao_worker.start()
    atexit.register(_shutdown)
    app.run(debug=True, use_reloader=False, port=5000)
