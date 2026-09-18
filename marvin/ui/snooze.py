import datetime
import time
import tkinter as tk

import customtkinter as ctk

from ..config import load_cfg
from ..database import db_adiar
from ..theme import get_modern_palette
from .window_position import position_near


def _position_near_marvin(
    window,
    companion,
):
    """
    Posiciona a janela de adiamento
    perto do MARVIN.
    """
    position_near(
        window,
        companion.root,
        companion.W,
        companion.H,
    )


class SnoozeWindow:

    WIDTH = 270
    HEIGHT = 380

    CUSTOM_WIDTH = 300
    CUSTOM_HEIGHT = 320

    OPTS = [
        ("5 minutos", 5),
        ("15 minutos", 15),
        ("30 minutos", 30),
        ("1 hora", 60),
    ]

    def __init__(
        self,
        root,
        companion,
        task,
    ):
        self.root = root
        self.comp = companion
        self.task = task

        self.custom_win = None
        self._custom_open = False

        # Guarda o balao atual para poder restaura-lo
        # caso o usuario cancele o adiamento.
        self._restore_bubble = ""

        current_task = (
            self.comp.reminded_task
        )

        self._owns_current_reminder = bool(
            self.task
            and current_task
            and current_task[0] == self.task[0]
        )

        if self._owns_current_reminder:
            self._restore_bubble = (
                self.comp.bubble
            )

            # Enquanto a janela de adiamento estiver aberta,
            # o balao antigo nao pode continuar interativo.
            self.comp.bubble = ""
            self.comp.b_timer = 0
            self.comp._bubble_deadline = None
            self.comp._bubble_mode = "normal"
            self.comp._bubble_hover = None

        self.tema = load_cfg().get(
            "tema",
            "escuro"
        )

        self.colors = get_modern_palette(
            self.tema,
            "interaction"
        )

        ctk.set_appearance_mode(
            "Light"
            if self.tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            root
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False
        )

        self.win.overrideredirect(
            True
        )

        self.win.attributes(
            "-topmost",
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self._build()

        _position_near_marvin(
            self.win,
            self.comp
        )

        self.win.bind(
            "<Escape>",
            lambda e: self._cancel()
        )

        self.win.bind(
            "<FocusOut>",
            self._on_focus_out
        )

        self.win.focus_force()


    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2,
        )

        # ====================================================
        # TOPO
        # ====================================================

        header = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
            padx=16,
            pady=(14, 4),
        )

        icon = ctk.CTkFrame(
            header,
            width=34,
            height=34,
            corner_radius=17,
            fg_color=self.colors["orange_bg"],
            border_width=1,
            border_color=self.colors["accent"],
        )

        icon.pack(
            side="left"
        )

        icon.pack_propagate(
            False
        )

        ctk.CTkLabel(
            icon,
            text="↻",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        title_wrap = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        title_wrap.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 0),
        )

        ctk.CTkLabel(
            title_wrap,
            text="Adiar tarefa",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            title_wrap,
            text="Escolha quando quer ser lembrado novamente",
            anchor="w",
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),
        ).pack(
            fill="x"
        )

        ctk.CTkButton(
            header,
            text="×",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["hover"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=18,
            ),
            command=self._cancel,
        ).pack(
            side="right",
            padx=(6, 0),
        )

        # ====================================================
        # TAREFA
        # ====================================================

        if self.task:
            task_card = ctk.CTkFrame(
                shell,
                fg_color=self.colors["bg"],
                corner_radius=9,
                border_width=1,
                border_color=self.colors["border"],
            )

            task_card.pack(
                fill="x",
                padx=16,
                pady=(8, 12),
            )

            ctk.CTkLabel(
                task_card,
                text=self.task[1],
                anchor="w",
                justify="left",
                wraplength=195,
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
            ).pack(
                fill="x",
                padx=11,
                pady=(8, 1),
            )

            ctk.CTkLabel(
                task_card,
                text=f"Horário original · {self.task[4][:5]}",
                anchor="w",
                text_color=self.colors["dim"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),
            ).pack(
                fill="x",
                padx=11,
                pady=(0, 8),
            )

        # ====================================================
        # OPCOES
        # ====================================================

        options = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        options.pack(
            fill="x",
            padx=16,
        )

        options.grid_columnconfigure(
            0,
            weight=1,
            uniform="snooze"
        )

        options.grid_columnconfigure(
            1,
            weight=1,
            uniform="snooze"
        )

        for i, (label, minutos) in enumerate(self.OPTS):

            row = i // 2
            column = i % 2

            button = ctk.CTkButton(
                options,
                text=label,
                height=42,
                corner_radius=9,
                fg_color="transparent",
                hover_color=self.colors["orange_bg"],
                border_width=1,
                border_color=self.colors["border"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
                command=lambda m=minutos:
                    self._snooze(m),
            )

            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(
                    (0, 4)
                    if column == 0
                    else (4, 0)
                ),
                pady=4,
            )

        ctk.CTkButton(
            shell,

            text="Outro horário...",

            height=34,

            corner_radius=8,

            fg_color="transparent",

            hover_color=self.colors[
                "orange_bg"
            ],

            border_width=1,

            border_color=self.colors[
                "accent"
            ],

            text_color=self.colors[
                "accent"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

            command=self._open_custom,

        ).pack(
            fill="x",
            padx=16,
            pady=(8, 0),
        )


        ctk.CTkButton(
            shell,
            text="Cancelar",
            height=30,
            corner_radius=7,
            fg_color="transparent",
            hover_color=self.colors["hover"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
            command=self._cancel,
        ).pack(
            fill="x",
            padx=16,
            pady=(8, 13),
        )


    def _on_focus_out(
        self,
        event=None
    ):
        # Pequeno atraso para permitir que o clique
        # nos botoes seja processado antes de fechar.
        try:
            self.win.after(
                100,
                self._close_if_focus_lost
            )
        except Exception:
            pass


    def _close_if_focus_lost(self):
        """
        Fecha a janela somente quando o foco
        realmente sair do SnoozeWindow.

        Trocar o foco entre botoes e outros
        widgets filhos nao deve fechar a janela.
        """
        if self._custom_open:
            return

        try:
            focus = self.win.focus_get()

            # Sem foco dentro da aplicacao.
            if focus is None:
                self._close()
                return

            try:
                focus_window = (
                    focus.winfo_toplevel()
                )
            except Exception:
                focus_window = None

            # Se o widget focado pertence a esta
            # mesma Toplevel, continua aberta.
            if focus_window == self.win:
                return

            self._close()

        except tk.TclError:
            # A janela pode ja ter sido destruida.
            pass

        except Exception:
            pass

    def _open_custom(self):
        """
        Abre uma janela para escolher uma data
        e horario especificos para o lembrete.
        """

        if not self._task_is_current():
            self._close()
            return

        if (
            self.custom_win is not None
            and self.custom_win.winfo_exists()
        ):
            try:
                self.custom_win.lift()
                self.custom_win.focus_force()
            except Exception:
                pass

            return

        self._custom_open = True

        # Uma hora a partir de agora e um bom
        # valor inicial para o formulario.
        default_dt = (
            datetime.datetime.now()
            + datetime.timedelta(hours=1)
        )

        self.custom_win = (
            ctk.CTkToplevel(
                self.root
            )
        )

        win = self.custom_win

        win.geometry(
            f"{self.CUSTOM_WIDTH}"
            f"x{self.CUSTOM_HEIGHT}"
        )

        win.resizable(
            False,
            False,
        )

        win.overrideredirect(
            True
        )

        win.attributes(
            "-topmost",
            True,
        )

        win.configure(
            fg_color=self.colors[
                "bg"
            ]
        )

        shell = ctk.CTkFrame(
            win,

            fg_color=self.colors[
                "card"
            ],

            corner_radius=16,

            border_width=1,

            border_color=self.colors[
                "border"
            ],
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2,
        )


        # --------------------------------------------
        # CABECALHO
        # --------------------------------------------

        header = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
            padx=16,
            pady=(15, 5),
        )

        title_wrap = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        title_wrap.pack(
            side="left",
            fill="x",
            expand=True,
        )

        ctk.CTkLabel(
            title_wrap,

            text="Adiar para",

            anchor="w",

            text_color=self.colors[
                "text"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),

        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            title_wrap,

            text=(
                "Escolha a data e o "
                "horário do lembrete"
            ),

            anchor="w",

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

        ).pack(
            fill="x"
        )

        ctk.CTkButton(
            header,

            text="×",

            width=30,
            height=30,

            corner_radius=8,

            fg_color="transparent",

            hover_color=self.colors[
                "hover"
            ],

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=18,
            ),

            command=self._close_custom,

        ).pack(
            side="right",
            padx=(6, 0),
        )


        # --------------------------------------------
        # FORMULARIO
        # --------------------------------------------

        form = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        form.pack(
            fill="x",
            padx=18,
            pady=(14, 0),
        )


        ctk.CTkLabel(
            form,

            text="Data",

            anchor="w",

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            fill="x",
            pady=(0, 4),
        )


        self._custom_date_var = (
            tk.StringVar(
                value=default_dt.strftime(
                    "%d/%m/%Y"
                )
            )
        )


        self._custom_date_entry = (
            ctk.CTkEntry(
                form,

                textvariable=(
                    self._custom_date_var
                ),

                height=36,

                corner_radius=8,

                border_width=1,

                border_color=self.colors[
                    "border"
                ],

                fg_color=self.colors[
                    "bg"
                ],

                text_color=self.colors[
                    "text"
                ],

                placeholder_text=(
                    "DD/MM/AAAA"
                ),

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                ),
            )
        )

        self._custom_date_entry.pack(
            fill="x",
        )


        ctk.CTkLabel(
            form,

            text="Horário",

            anchor="w",

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            fill="x",
            pady=(10, 4),
        )


        self._custom_time_var = (
            tk.StringVar(
                value=default_dt.strftime(
                    "%H:%M"
                )
            )
        )


        self._custom_time_entry = (
            ctk.CTkEntry(
                form,

                textvariable=(
                    self._custom_time_var
                ),

                height=36,

                corner_radius=8,

                border_width=1,

                border_color=self.colors[
                    "border"
                ],

                fg_color=self.colors[
                    "bg"
                ],

                text_color=self.colors[
                    "text"
                ],

                placeholder_text="HH:MM",

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                ),
            )
        )

        self._custom_time_entry.pack(
            fill="x",
        )


        self._custom_error = (
            ctk.CTkLabel(
                form,

                text="",

                anchor="w",

                text_color=self.colors[
                    "accent"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),
            )
        )

        self._custom_error.pack(
            fill="x",
            pady=(5, 0),
        )


        # --------------------------------------------
        # ACOES
        # --------------------------------------------

        actions = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
            padx=18,
            pady=(8, 15),
        )

        actions.grid_columnconfigure(
            0,
            weight=1,
        )

        actions.grid_columnconfigure(
            1,
            weight=1,
        )


        ctk.CTkButton(
            actions,

            text="Voltar",

            height=34,

            corner_radius=8,

            fg_color="transparent",

            hover_color=self.colors[
                "hover"
            ],

            border_width=1,

            border_color=self.colors[
                "border"
            ],

            text_color=self.colors[
                "text"
            ],

            command=self._close_custom,

        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )


        ctk.CTkButton(
            actions,

            text="Adiar",

            height=34,

            corner_radius=8,

            fg_color=self.colors[
                "accent"
            ],

            hover_color=self.colors[
                "accent_hover"
            ],

            text_color="#FFFFFF",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

            command=self._apply_custom,

        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(4, 0),
        )


        win.bind(
            "<Escape>",
            lambda e:
                self._close_custom()
        )

        win.bind(
            "<Return>",
            lambda e:
                self._apply_custom()
        )


        # Esconde a janela de opcoes rapidas
        # enquanto a personalizada estiver ativa.
        try:
            self.win.withdraw()
        except Exception:
            pass


        _position_near_marvin(
            win,
            self.comp,
        )

        win.lift()
        win.focus_force()

        try:
            self._custom_date_entry.focus_set()
            self._custom_date_entry.select_range(
                0,
                "end",
            )
        except Exception:
            pass


    def _close_custom(self):
        """
        Fecha somente o formulario personalizado
        e retorna para as opcoes rapidas.
        """

        win = self.custom_win

        self.custom_win = None
        self._custom_open = False

        if win is not None:
            try:
                win.destroy()
            except Exception:
                pass

        try:
            if self.win.winfo_exists():
                self.win.deiconify()

                _position_near_marvin(
                    self.win,
                    self.comp,
                )

                self.win.lift()
                self.win.focus_force()

        except Exception:
            pass


    def _apply_custom(self):
        """
        Valida data/hora e aplica o adiamento.
        """

        if not self._task_is_current():
            self._close()
            return

        data_text = (
            self._custom_date_var
            .get()
            .strip()
        )

        hora_text = (
            self._custom_time_var
            .get()
            .strip()
        )

        try:
            new_dt = (
                datetime.datetime.strptime(
                    (
                        f"{data_text} "
                        f"{hora_text}"
                    ),
                    "%d/%m/%Y %H:%M",
                )
            )

        except ValueError:
            self._custom_error.configure(
                text=(
                    "Use DD/MM/AAAA "
                    "e HH:MM."
                )
            )
            return


        agora = datetime.datetime.now()

        if new_dt <= agora:
            self._custom_error.configure(
                text=(
                    "Escolha um horário "
                    "no futuro."
                )
            )
            return


        self._snooze_at(
            new_dt
        )


    def _task_is_current(self):
        """Confirma que esta janela ainda controla o lembrete atual."""

        current_task = (
            self.comp.reminded_task
        )

        return bool(
            self.task
            and current_task
            and current_task[0] == self.task[0]
        )


    def _cancel(self):
        """Fecha o adiamento e devolve o controle ao balao."""

        if self._task_is_current():

            self.comp.bubble = (
                self._restore_bubble
                or self.task[1]
            )

            self.comp._bubble_mode = "alert"
            self.comp._bubble_hover = None

            # Reinicia a contagem da reacao de espera,
            # pois o usuario voltou ao alerta.
            self.comp._reminder_started_at = (
                time.monotonic()
            )

            self.comp._waiting_reaction_stage = 0

        self._close()


    def _close(self):

        self._custom_open = False

        custom_win = (
            self.custom_win
        )

        self.custom_win = None

        if custom_win is not None:
            try:
                custom_win.destroy()
            except Exception:
                pass

        try:
            self.win.destroy()

        except Exception:
            pass


    def _snooze(
        self,
        minutes
    ):

        if not self._task_is_current():
            self._close()
            return

        new_dt = (
            datetime.datetime.now()
            + datetime.timedelta(
                minutes=minutes
            )
        )

        self._snooze_at(
            new_dt
        )


    def _snooze_at(
        self,
        new_dt,
    ):
        """
        Aplica um datetime absoluto de adiamento.

        Tanto as opcoes rapidas quanto o horario
        personalizado passam por este metodo.
        """

        if not self._task_is_current():
            self._close()
            return

        if self.task:
            db_adiar(
                self.task[0],

                new_dt.strftime(
                    "%Y-%m-%d"
                ),

                new_dt.strftime(
                    "%H:%M"
                ),
            )

        self.comp._next_reminder()


        hoje = (
            datetime.datetime.now()
            .date()
        )

        if new_dt.date() == hoje:
            mensagem = (
                "Adiado para "
                f"{new_dt.strftime('%H:%M')}."
            )

        else:
            mensagem = (
                "Adiado para "
                f"{new_dt.strftime('%d/%m')} "
                "às "
                f"{new_dt.strftime('%H:%M')}."
            )


        self.comp.say(
            mensagem,
            "talking",
            3000,
        )

        self._close()





#  PERSONAGEM PRINCIPAL — MARVIN
