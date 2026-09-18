import tkinter as tk

import customtkinter as ctk

from ..theme import get_modern_palette


class WaitingPhrasesWindow:

    WIDTH = 430
    HEIGHT = 520

    DEFAULTS = [
        "Ei... {tarefa}",
        "Vai fazer ou adiar? {tarefa}",
        "Ainda estou esperando: {tarefa}",
    ]

    def __init__(
        self,
        parent,
        companion,
        *,
        config,
        positioner,
        save_config,
    ):
        self.comp = companion
        self.cfg = config

        self._positioner = positioner
        self._save_config = save_config

        tema = self.cfg.get(
            "tema",
            "escuro",
        )

        self.colors = (
            get_modern_palette(
                tema,
                "settings",
            )
        )

        ctk.set_appearance_mode(
            "Light"
            if tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            parent
        )

        self.win.withdraw()

        self.win.overrideredirect(
            True
        )

        self.win.geometry(
            f"{self.WIDTH}"
            f"x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False,
        )

        self.win.attributes(
            "-topmost",
            True,
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self.win.transient(
            parent
        )

        self._drag_x = 0
        self._drag_y = 0

        self._build()

        self.win.update_idletasks()

        self._positioner(
            self.win,
            self.comp,
        )

        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

        self.win.bind(
            "<Escape>",
            lambda event:
                self.win.destroy(),
        )


    def _drag_start(
        self,
        event,
    ):
        self._drag_x = (
            event.x_root
            - self.win.winfo_x()
        )

        self._drag_y = (
            event.y_root
            - self.win.winfo_y()
        )


    def _drag_move(
        self,
        event,
    ):
        x = (
            event.x_root
            - self._drag_x
        )

        y = (
            event.y_root
            - self._drag_y
        )

        self.win.geometry(
            f"+{x}+{y}"
        )


    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["card"],
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


        # ====================================================
        # TITLEBAR
        # ====================================================

        titlebar = ctk.CTkFrame(
            shell,
            height=48,
            corner_radius=0,
            fg_color="transparent",
        )

        titlebar.pack(
            fill="x",
            padx=12,
            pady=(4, 0),
        )

        titlebar.pack_propagate(
            False
        )


        mark = ctk.CTkLabel(
            titlebar,
            text="",
            width=6,
        )

        mark.pack(
            side="left",
            padx=(5, 5),
        )


        title = ctk.CTkLabel(
            titlebar,
            text=(
                "MARVIN - "
                "FRASES DE ESPERA"
            ),
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        )

        title.pack(
            side="left"
        )


        close_button = ctk.CTkButton(
            titlebar,
            text="x",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors[
                "surface"
            ],
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
            ),
            command=self.win.destroy,
        )

        close_button.pack(
            side="right"
        )


        for widget in (
            titlebar,
            mark,
            title,
        ):
            widget.bind(
                "<ButtonPress-1>",
                self._drag_start,
            )

            widget.bind(
                "<B1-Motion>",
                self._drag_move,
            )


        ctk.CTkFrame(
            shell,
            height=1,
            corner_radius=0,
            fg_color=self.colors[
                "border"
            ],
        ).pack(
            fill="x"
        )


        # ====================================================
        # CONTEUDO
        # ====================================================

        body = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        body.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(14, 10),
        )


        ctk.CTkLabel(
            body,
            text="Frases de espera",
            anchor="w",
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20,
                weight="bold",
            ),
        ).pack(
            fill="x"
        )


        ctk.CTkLabel(
            body,
            text=(
                "Personalize as reacoes "
                "do MARVIN enquanto um lembrete "
                "aguarda sua resposta."
            ),
            anchor="w",
            justify="left",
            wraplength=380,
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        ).pack(
            fill="x",
            pady=(2, 12),
        )


        help_card = ctk.CTkFrame(
            body,
            fg_color=self.colors[
                "surface"
            ],
            corner_radius=8,
            border_width=1,
            border_color=self.colors[
                "border"
            ],
        )

        help_card.pack(
            fill="x",
            pady=(0, 12),
        )


        ctk.CTkLabel(
            help_card,
            text=(
                "Use {tarefa} onde quiser "
                "mostrar o nome da tarefa."
            ),
            anchor="w",
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        ).pack(
            fill="x",
            padx=11,
            pady=8,
        )


        frases = self.cfg.get(
            "frases_waiting",
            self.DEFAULTS,
        )

        if (
            not isinstance(
                frases,
                list,
            )
            or len(frases) < 3
        ):
            frases = list(
                self.DEFAULTS
            )


        self.vars = []

        labels = [
            "Primeira reacao",
            "Segunda reacao",
            "Terceira reacao",
        ]


        for index, label in enumerate(
            labels
        ):

            ctk.CTkLabel(
                body,
                text=label,
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
                pady=(
                    (0, 4)
                    if index == 0
                    else (8, 4)
                ),
            )


            var = tk.StringVar(
                value=str(
                    frases[index]
                )
            )

            self.vars.append(
                var
            )


            entry = ctk.CTkEntry(
                body,
                textvariable=var,
                height=36,
                corner_radius=8,
                border_width=1,
                border_color=self.colors[
                    "border"
                ],
                fg_color=self.colors[
                    "surface"
                ],
                text_color=self.colors[
                    "text"
                ],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                ),
            )

            entry.pack(
                fill="x"
            )


        # ====================================================
        # FOOTER
        # ====================================================

        footer = ctk.CTkFrame(
            shell,
            fg_color=self.colors[
                "card"
            ],
            corner_radius=0,
        )

        footer.pack(
            fill="x"
        )


        ctk.CTkFrame(
            footer,
            height=1,
            corner_radius=0,
            fg_color=self.colors[
                "border"
            ],
        ).pack(
            fill="x"
        )


        actions = ctk.CTkFrame(
            footer,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
            padx=18,
            pady=12,
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
            text="Restaurar padrao",
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors[
                "surface"
            ],
            border_width=1,
            border_color=self.colors[
                "border"
            ],
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            command=self._restaurar,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
        )


        ctk.CTkButton(
            actions,
            text="Salvar alteracoes",
            height=40,
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
                size=10,
                weight="bold",
            ),
            command=self._salvar,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
        )


    def _restaurar(self):

        for var, texto in zip(
            self.vars,
            self.DEFAULTS,
        ):
            var.set(
                texto
            )


    def _salvar(self):

        frases = []

        for index, var in enumerate(
            self.vars
        ):
            texto = (
                var.get()
                .strip()
            )

            if not texto:
                texto = (
                    self.DEFAULTS[
                        index
                    ]
                )

            frases.append(
                texto
            )


        self.cfg[
            "frases_waiting"
        ] = frases


        self._save_config(
            self.cfg
        )


        self.comp.say(
            "Frases salvas!",
            "talking",
            2000,
        )


        self.win.destroy()
