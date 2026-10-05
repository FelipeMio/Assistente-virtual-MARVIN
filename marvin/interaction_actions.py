import datetime
import time


class InteractionActionController:
    """
    Executa as acoes disparadas pelas
    interacoes de mouse do MARVIN.
    """

    def __init__(
        self,
        root,
        companion,
        *,
        get_bubble_mode,
        set_bubble_mode,
        set_bubble_hover,
        reminder_active,
        current_reminder,
        complete_task,
        next_reminder,
        set_reminder_started_at,
        set_waiting_stage,
        snooze_factory,
        panel_factory,
        db_snooze,
    ):
        self.root = root
        self.companion = companion

        self._get_bubble_mode = (
            get_bubble_mode
        )

        self._set_bubble_mode = (
            set_bubble_mode
        )

        self._set_bubble_hover = (
            set_bubble_hover
        )

        self._reminder_active = (
            reminder_active
        )

        self._current_reminder = (
            current_reminder
        )

        self._complete_task = (
            complete_task
        )

        self._next_reminder = (
            next_reminder
        )

        self._set_reminder_started_at = (
            set_reminder_started_at
        )

        self._set_waiting_stage = (
            set_waiting_stage
        )

        self._snooze_factory = (
            snooze_factory
        )

        self._panel_factory = (
            panel_factory
        )

        self._db_snooze = (
            db_snooze
        )

        self._panel_open = False


    # ========================================================
    # BUBBLE ACTIONS
    # ========================================================

    def handle_bubble_button(
        self,
        button,
    ):
        if button == "complete":
            self._complete_task()
            return


        if button == "snooze":
            self._set_reminder_started_at(
                None
            )

            self._set_waiting_stage(
                0
            )

            self._set_bubble_hover(
                None
            )

            task = (
                self._current_reminder()
            )

            if task:
                self._snooze_factory(
                    self.root,
                    self.companion,
                    task,
                )

            return


        if button in (
            "5",
            "15",
            "30",
            "60",
        ):
            self._quick_snooze(
                button
            )

            return


        if button == "back":
            self._set_reminder_started_at(
                time.monotonic()
            )

            self._set_waiting_stage(
                0
            )

            self._set_bubble_mode(
                "alert"
            )

            self._set_bubble_hover(
                None
            )


    def _quick_snooze(
        self,
        button,
    ):
        task = (
            self._current_reminder()
        )

        if not task:
            return


        minutes = int(
            button
        )


        new_time = (
            datetime.datetime.now()
            + datetime.timedelta(
                minutes=minutes
            )
        )


        self._db_snooze(
            task[0],
            new_time.strftime(
                "%Y-%m-%d"
            ),
            new_time.strftime(
                "%H:%M"
            ),
        )


        self._set_bubble_mode(
            "normal"
        )

        self._set_bubble_hover(
            None
        )

        self._next_reminder()


    # ========================================================
    # INTERACTION PANEL
    # ========================================================

    def open_panel(
        self,
        event=None,
    ):
        if self._get_bubble_mode() in (
            "alert",
            "snooze",
        ):
            return


        if self._reminder_active():
            return


        if self._panel_open:
            return


        self._panel_open = True


        try:
            panel = (
                self._panel_factory(
                    self.root,
                    self.companion,
                    mode="idle",
                )
            )

        except Exception as exc:
            self._panel_open = False

            print(
                "[MARVIN] Erro ao abrir "
                f"InteractionPanel: {exc}"
            )

            return


        panel.win.bind(
            "<Destroy>",
            self._panel_destroyed,
        )


    def _panel_destroyed(
        self,
        event=None,
    ):
        self._panel_open = False
