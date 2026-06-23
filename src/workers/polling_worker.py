import logging
import threading
from src.services.notaas.polling_service import match_jobs_processing

logger = logging.getLogger(__name__)

class PollingWorker:
    def __init__(self, intervalo_poll: float = 15.0):
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._intervalo_poll = intervalo_poll

    def _loop(self) -> None:
        logger.info("polling worker iniciado")

        while not self._stop_event.is_set():
            try:
                match_jobs_processing()

            except Exception:
                logger.exception("erro no ciclo de reconciliacao")
            self._stop_event.wait(timeout=self._intervalo_poll)
        logger.info("polling worker finalizado")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)