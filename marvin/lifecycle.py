import logging
import threading
import tkinter as tk


logger = logging.getLogger(
    "marvin.lifecycle"
)


class LifecycleController:
    """
    Centraliza a inicializacao e o encerramento
    dos servicos principais do MARVIN.
    """

    def __init__(
        self,
        root,
        companion,
        *,
        tray,
        reminders,
        routine,
        notification_factory,
        set_notifications,
        load_extensions,
        cleanup_database,
        start_day,
        start_animation,
        stop_animation,
        start_day_delay_ms=900,
    ):
        self.root = root
        self.companion = companion

        self.tray = tray
        self.reminders = reminders
        self.routine = routine

        self._notification_factory = (
            notification_factory
        )

        self._set_notifications = (
            set_notifications
        )

        self._load_extensions = (
            load_extensions
        )

        self._cleanup_database = (
            cleanup_database
        )

        self._start_day = (
            start_day
        )

        self._start_animation = (
            start_animation
        )

        self._stop_animation = (
            stop_animation
        )

        self.start_day_delay_ms = int(
            start_day_delay_ms
        )

        self.extensions = []

        self._cleanup_thread = None
        self._start_day_job = None

        self._started = False
        self._stopped = False


    @property
    def started(self):
        return self._started


    @property
    def stopped(self):
        return self._stopped


    # ========================================================
    # START
    # ========================================================

    def start(self):
        if self._started:
            return

        self._started = True
        self._stopped = False


        # Todos os timers e servicos passam
        # a possuir um unico owner.
        self.routine.start()

        self.tray.start()

        self._start_animation()

        self.reminders.start()


        notifications = (
            self._notification_factory()
        )

        self._set_notifications(
            notifications
        )


        try:
            loaded = (
                self._load_extensions(
                    self.companion
                )
            )

        except Exception:
            logger.exception(
                "Erro ao carregar extensoes."
            )

            loaded = []


        if loaded:
            self.extensions = list(
                loaded
            )

        else:
            self.extensions = []


        self._cleanup_thread = (
            threading.Thread(
                target=self._run_cleanup,
                daemon=True,
                name="marvin-db-cleanup",
            )
        )

        self._cleanup_thread.start()


        try:
            self._start_day_job = (
                self.root.after(
                    self.start_day_delay_ms,
                    self._run_start_day,
                )
            )

        except tk.TclError:
            self._start_day_job = None



    def _run_cleanup(self):
        try:
            self._cleanup_database()

        except Exception:
            logger.exception(
                "Erro na limpeza do banco."
            )


    def _run_start_day(self):
        self._start_day_job = None

        if self._stopped:
            return

        try:
            self._start_day()

        except Exception:
            logger.exception(
                "Erro na rotina inicial."
            )


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):
        if self._stopped:
            return

        self._stopped = True


        self._cancel_start_day()

        self._stop_service(
            self.routine,
            "rotina",
        )

        self._stop_callback(
            self._stop_animation,
            "animacao",
        )

        self._stop_extensions()

        self._stop_service(
            self.reminders,
            "lembretes",
        )

        self._stop_service(
            self.tray,
            "bandeja",
        )

        self._join_cleanup_thread()



    def _cancel_start_day(self):
        job = self._start_day_job
        self._start_day_job = None

        if job is None:
            return

        try:
            self.root.after_cancel(
                job
            )

        except Exception:
            pass


    def _stop_extensions(self):
        for extension in reversed(
            self.extensions
        ):
            stop = getattr(
                extension,
                "stop",
                None,
            )

            if not callable(stop):
                continue

            try:
                stop()

            except Exception:
                logger.exception(
                    "Erro ao encerrar extensao %s.",
                    type(extension).__name__,
                )


    def _join_cleanup_thread(self):
        thread = self._cleanup_thread

        if thread is None:
            return

        if thread is threading.current_thread():
            return

        if thread.is_alive():
            thread.join(
                timeout=2.0
            )

        if not thread.is_alive():
            self._cleanup_thread = None


    @staticmethod
    def _stop_callback(
        callback,
        name,
    ):
        if not callable(callback):
            return

        try:
            callback()

        except Exception:
            logger.exception(
                "Erro ao encerrar %s.",
                name,
            )


    @staticmethod
    def _stop_service(
        service,
        name,
    ):
        stop = getattr(
            service,
            "stop",
            None,
        )

        if not callable(stop):
            return

        try:
            stop()

        except Exception:
            logger.exception(
                "Erro ao encerrar %s.",
                name,
            )
