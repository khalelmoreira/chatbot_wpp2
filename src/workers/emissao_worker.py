import time
import threading
import logging
from src.managers.nfs.nf_worker_manager import NfsWorkerManager
from src.services.worker.processar_job import processar_job

logger = logging.getLogger(__name__)

class EmissaoWorker:
    def __init__(self, intervalo_poll: float = 2.0):
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._intevalo_poll = intervalo_poll
        
    def _loop(self) -> None:

        logger.info("Worker de emissao iniciado")

        while not self._stop_event.is_set():

            try:
                manager = NfsWorkerManager.reserva_job()
            except Exception:
                logger.exception("erro ao reservar job")
                self._stop_event.wait(timeout=self._intevalo_poll)
                continue

            if not manager:
                self._stop_event.wait(timeout=self._intevalo_poll)
                continue

            espera = processar_job(manager)
            self._stop_event.wait(timeout=espera or self._intevalo_poll)
        
        logger.info("worker finalizado")

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
            if self._thread.is_alive():
                logger.warning("worker não finalizou dentro do timeout")

