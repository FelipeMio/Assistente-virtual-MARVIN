import datetime
import threading
import tkinter as tk


class ReminderQueue:
    """
    Fila dos lembretes atualmente ativos.

    Implementa as operacoes basicas de uma lista
    para manter compatibilidade temporaria com
    componentes antigos do MARVIN.
    """

    def __init__(self):
        self._items = []


    def __bool__(self):
        return bool(
            self._items
        )


    def __len__(self):
        return len(
            self._items
        )


    def __iter__(self):
        return iter(
            self._items
        )


    def __getitem__(
        self,
        index,
    ):
        return self._items[
            index
        ]


    def append(
        self,
        row,
    ):
        self._items.append(
            row
        )


    def pop(
        self,
        index=-1,
    ):
        return self._items.pop(
            index
        )


    def clear(self):
        self._items.clear()


    def peek(self):
        if not self._items:
            return None

        return self._items[0]


    def pop_current(self):
        if not self._items:
            return None

        return self._items.pop(0)


    def contains_task_id(
        self,
        task_id,
    ):
        return any(
            row[0] == task_id
            for row in self._items
        )



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

        # Fila dos lembretes entregues para a UI.
        self.queue = ReminderQueue()

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


                # Tarefas recorrentes usam a flag "lembrado"
                # para evitar repetir a mesma ocorrencia.
                #
                # Tarefas comuns nao podem ser descartadas por
                # essa flag: se o MARVIN foi fechado antes de o
                # usuario concluir/adiar, o alerta precisa voltar
                # na proxima execucao.
                if (
                    lemb
                    and rep != "Nunca"
                ):
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


                # Tarefa comum:
                # depois que vence, continua pendente ate
                # o usuario concluir ou adiar.
                if rep == "Nunca":
                    due = (
                        diff >= 0
                    )

                # Tarefa recorrente:
                # mantem a janela curta da ocorrencia atual.
                else:
                    due = (
                        0 <= diff < 90
                    )


                if (
                    due
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
