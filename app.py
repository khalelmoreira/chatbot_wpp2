from flask import Flask
import logging
import atexit
from src.workers import EmissaoWorker
from src.database.tables_db import init_db
from dotenv import load_dotenv
from src.routes import wpp_bp, ntaas_bp

load_dotenv()
logger = logging.getLogger(__name__)
emissao_worker = EmissaoWorker(intervalo_poll=2.0)

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(wpp_bp)
    app.register_blueprint(ntaas_bp)
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
