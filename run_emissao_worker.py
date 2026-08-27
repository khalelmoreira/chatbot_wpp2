import logging
import signal
import threading

from dotenv import load_dotenv

from src.database.tables_db import init_db
from src.logging_config import setup_logging
from src.workers import EmissaoWorker

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    init_db()
    worker = EmissaoWorker(intervalo_poll=2.0)
    worker.start()

    stop_event = threading.Event()

    def _shutdown(signum, frame):
        logger.info("sinal de shutdown recebido")
        stop_event.set()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    stop_event.wait()
    worker.stop()


if __name__ == "__main__":
    main()
