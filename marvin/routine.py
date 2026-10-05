import datetime
import random


class RoutineController:
    """
    Controla o inicio do dia, resumo diario
    e falas espontaneas do MARVIN.
    """

    def __init__(
        self,
        root,
        *,
        config,
        save_config,
        list_tasks,
        streak_today,
        idle_phrases,
        greeting_factory,
        say,
        show_marvin,
        reminder_active,
        compact_active,
        expand_compact,
        can_idle_speak,
        set_state,
        set_bubble_mode,
        set_bubble_hover,
    ):
        self.root = root

        self.config = config
        self._save_config = save_config

        self._list_tasks = list_tasks
        self._streak_today = streak_today

        self._idle_phrases = idle_phrases
        self._greeting_factory = (
            greeting_factory
        )

        self._say = say
        self._show_marvin = show_marvin

        self._reminder_active = (
            reminder_active
        )

        self._compact_active = (
            compact_active
        )

        self._expand_compact = (
            expand_compact
        )

        self._can_idle_speak = (
            can_idle_speak
        )

        self._set_state = set_state

        self._set_bubble_mode = (
            set_bubble_mode
        )

        self._set_bubble_hover = (
            set_bubble_hover
        )

        self._idle_job = None
        self._stopped = False


    # ========================================================
    # TASK DATE
    # ========================================================

    @staticmethod
    def task_due_today(
        row,
        today,
    ):
        try:
            (
                tid,
                text,
                desc,
                date,
                hour,
                repeat,
                completed,
                reminded,
            ) = row

        except Exception:
            return False


        if completed:
            return False


        try:
            base_date = (
                datetime.date
                .fromisoformat(
                    date
                )
            )

        except Exception:
            return False


        if base_date > today:
            return False


        if repeat == "Nunca":
            return (
                base_date == today
            )


        if repeat == "Todo dia":
            return True


        if repeat == "Toda semana":
            return (
                base_date.weekday()
                == today.weekday()
            )


        if repeat == "Seg/Qua/Sex":
            return (
                today.weekday()
                in (
                    0,
                    2,
                    4,
                )
            )


        if repeat == "Seg a Sex":
            return (
                today.weekday() < 5
            )


        if repeat == "Fins de semana":
            return (
                today.weekday() >= 5
            )


        return False


    # ========================================================
    # START OF DAY
    # ========================================================

    def start_day(self):
        today = (
            datetime.date.today()
            .isoformat()
        )


        if (
            self.config.get(
                "ultimo_resumo_dia"
            )
            != today
        ):
            self.summary()

        else:
            self.initial_greeting()


    # ========================================================
    # DAILY SUMMARY
    # ========================================================

    def summary(self):
        # Never replace an active reminder.
        if self._reminder_active():
            return


        self._show_marvin()


        if self._compact_active():
            self._expand_compact()


        today = (
            datetime.date.today()
        )

        today_iso = (
            today.isoformat()
        )


        try:
            rows = (
                self._list_tasks()
            )

        except Exception as exc:
            print(
                "[MARVIN] Erro ao gerar "
                f"resumo: {exc}"
            )

            return


        pending_today = 0
        overdue = 0


        for row in rows:

            try:
                (
                    tid,
                    text,
                    desc,
                    date,
                    hour,
                    repeat,
                    completed,
                    reminded,
                ) = row

            except Exception:
                continue


            if completed:
                continue


            if self.task_due_today(
                row,
                today,
            ):
                pending_today += 1
                continue


            if repeat == "Nunca":
                try:
                    task_date = (
                        datetime.date
                        .fromisoformat(
                            date
                        )
                    )

                    if task_date < today:
                        overdue += 1

                except Exception:
                    pass


        completed_today = (
            self._streak_today()
        )


        hour = (
            datetime.datetime.now()
            .hour
        )


        if hour < 12:
            greeting = "Bom dia!"

        elif hour < 18:
            greeting = "Boa tarde!"

        else:
            greeting = "Boa noite!"


        parts = []


        if pending_today == 0:
            parts.append(
                "Nenhuma tarefa pendente para hoje."
            )

        elif pending_today == 1:
            parts.append(
                "Voce tem 1 tarefa para hoje."
            )

        else:
            parts.append(
                f"Voce tem {pending_today} "
                "tarefas para hoje."
            )


        if overdue == 1:
            parts.append(
                "1 esta atrasada."
            )

        elif overdue > 1:
            parts.append(
                f"{overdue} estao atrasadas."
            )


        if completed_today == 1:
            parts.append(
                "1 concluida hoje."
            )

        elif completed_today > 1:
            parts.append(
                f"{completed_today} "
                "concluidas hoje."
            )


        message = (
            greeting
            + " "
            + " ".join(parts)
        )


        self.config[
            "ultimo_resumo_dia"
        ] = today_iso


        self._save_config(
            self.config
        )


        self._set_bubble_mode(
            "normal"
        )

        self._set_bubble_hover(
            None
        )


        self._say(
            message,
            "talking",
            8000,
        )


    # ========================================================
    # INITIAL GREETING
    # ========================================================

    def initial_greeting(self):
        self._set_state(
            "idle"
        )


        rows = (
            self._list_tasks()
        )


        pending = len(
            [
                row
                for row in rows
                if not row[6]
            ]
        )


        self._say(
            self._greeting_factory(
                pending
            ),
            "talking",
            5000,
        )


    # ========================================================
    # IDLE SPEECH
    # ========================================================

    def start(self):
        self._stopped = False
        self.schedule_idle()


    def stop(self):
        self._stopped = True

        job = self._idle_job
        self._idle_job = None

        if job is None:
            return

        try:
            self.root.after_cancel(
                job
            )

        except Exception:
            pass

    def idle_interval_ms(self):
        try:
            seconds = int(
                self.config.get(
                    "idle_interval_seconds",
                    300,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            seconds = 300


        return max(
            0,
            seconds,
        ) * 1000


    def schedule_idle(self):
        if self._stopped:
            return

        if self._idle_job is not None:

            try:
                self.root.after_cancel(
                    self._idle_job
                )

            except Exception:
                pass


            self._idle_job = None


        interval = (
            self.idle_interval_ms()
        )


        if interval <= 0:
            return


        self._idle_job = (
            self.root.after(
                interval,
                self._idle_message,
            )
        )



    def _idle_message(self):
        self._idle_job = None

        if self._stopped:
            return


        if self.idle_interval_ms() <= 0:
            return


        if self._can_idle_speak():

            self._set_bubble_mode(
                "normal"
            )

            self._set_bubble_hover(
                None
            )


            phrases = (
                self._idle_phrases()
            )


            self._say(
                random.choice(
                    phrases
                ),
                "talking",
                10000,
            )


        self.schedule_idle()

