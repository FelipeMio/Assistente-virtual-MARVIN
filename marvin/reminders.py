import datetime
import threading
import tkinter as tk


class ReminderService:
    """
    Monitora tarefas pendentes em background
    e entrega lembretes vencidos para a thread
    principal do Tkinter.
    """

    def __init__(
        self,
        root,
        *,
        list_tasks,
        on_due,
        poll_seconds=1.0,
    ):
        self.root = root
        self._list_tasks = list_tasks
        self._on_due = on_due

        self.poll_seconds = float(
            poll_seconds
        )

        self._stop_event = (
            threading.Event()
        )

        self._thread = None


    @property
    def running(self):
        return (
            self._thread is not None
            and self._thread.is_alive()
        )


    def start(self):
        if self.running:
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="marvin-reminders",
            daemon=True,
        )

        self._thread.start()


    def stop(self):
        self._stop_event.set()


    def _run(self):
        while not self._stop_event.wait(
            self.poll_seconds
        ):
            now = (
                datetime.datetime.now()
            )

            today = now.strftime(
                "%Y-%m-%d"
            )

            try:
                rows = self._list_tasks(
                    apenas_pendentes=True
                )

            except Exception as exc:
                print(
                    "[MARVIN] Erro ao listar "
                    f"lembretes: {exc}"
                )

                continue


            for row in rows:

                if self._stop_event.is_set():
                    break


                try:
                    (
                        tid,
                        texto,
                        desc,
                        data,
                        hora,
                        rep,
                        conc,
                        lemb,
                    ) = row

                except Exception:
                    continue


                if lemb:
                    continue


                try:
                    hora_s = hora[:5]

                except (TypeError, IndexError):
                    continue


                try:
                    data_original = (
                        datetime.date
                        .fromisoformat(
                            data
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue


                hoje_data = now.date()


                if hoje_data < data_original:
                    continue


                if rep == "Nunca":
                    data_lembrete = (
                        data_original
                    )

                else:
                    if not self.should_remind(
                        rep,
                        data,
                        now,
                        today,
                    ):
                        continue

                    data_lembrete = (
                        hoje_data
                    )


                try:
                    hora_obj = (
                        datetime.datetime
                        .strptime(
                            hora_s,
                            "%H:%M",
                        )
                        .time()
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue


                task_dt = (
                    datetime.datetime
                    .combine(
                        data_lembrete,
                        hora_obj,
                    )
                )


                diff = (
                    now - task_dt
                ).total_seconds()


                if (
                    0 <= diff < 90
                    and not self._stop_event.is_set()
                ):
                    try:
                        self.root.after(
                            0,
                            lambda r=row:
                                self._on_due(r),
                        )

                    except tk.TclError:
                        return


    @staticmethod
    def should_remind(
        rep,
        data,
        now,
        today,
    ):
        if rep == "Nunca":
            return (
                data == today
            )

        if rep == "Todo dia":
            return True

        if rep == "Toda semana":
            try:
                return (
                    datetime.date
                    .fromisoformat(
                        data
                    )
                    .weekday()
                    == now.weekday()
                )

            except Exception:
                return False

        if rep == "Seg/Qua/Sex":
            return (
                now.weekday()
                in (
                    0,
                    2,
                    4,
                )
            )

        if rep == "Seg a Sex":
            return (
                now.weekday() < 5
            )

        if rep == "Fins de semana":
            return (
                now.weekday() >= 5
            )

        return False
