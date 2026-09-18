import tkinter as tk


class WaitingPhrasesWindow:
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
        palette,
        make_window,
        positioner,
        header_factory,
        save_config,
    ):
        self.comp = companion

        self.cfg = config
        self.colors = palette

        self._make_window = (
            make_window
        )

        self._positioner = (
            positioner
        )

        self._header_factory = (
            header_factory
        )

        self._save_config = (
            save_config
        )

        self.win = self._make_window(
            parent,
            "Frases de espera",
            430,
            360
        )

        self._build()

        self._positioner(
            self.win,
            self.comp
        )


    def _build(self):
        w = self.win

        self._header_factory(
            w,
            "Frases de espera"
        )

        body = tk.Frame(
            w,
            bg=self.colors["win_bg"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=12
        )

        tk.Label(
            body,
            text=(
                "Use {tarefa} onde quiser que "
                "apareca o nome da tarefa."
            ),
            bg=self.colors["win_bg"],
            fg=self.colors["dim"],
            font=("Consolas", 8),
            wraplength=380,
            justify="left"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        frases = self.cfg.get(
            "frases_waiting",
            self.DEFAULTS
        )

        if (
            not isinstance(frases, list)
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

        for i, label in enumerate(labels):

            tk.Label(
                body,
                text=label,
                bg=self.colors["win_bg"],
                fg=self.colors["dim"],
                font=(
                    "Consolas",
                    8,
                    "bold"
                )
            ).pack(
                anchor="w",
                pady=(5, 2)
            )

            var = tk.StringVar(
                value=str(frases[i])
            )

            self.vars.append(var)

            entry = tk.Entry(
                body,
                textvariable=var,
                bg=self.colors["panel"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief="flat",
                bd=0,
                font=("Consolas", 8)
            )

            entry.pack(
                fill="x",
                ipady=6
            )

        botoes = tk.Frame(
            body,
            bg=self.colors["win_bg"]
        )

        botoes.pack(
            anchor="w",
            pady=(14, 0)
        )

        tk.Button(
            botoes,
            text="Salvar",
            bg=self.colors["green"],
            fg=self.colors["win_bg"],
            bd=0,
            padx=14,
            pady=7,
            font=(
                "Consolas",
                9,
                "bold"
            ),
            cursor="hand2",
            activebackground=self.colors["accent"],
            command=self._salvar
        ).pack(
            side="left"
        )

        tk.Button(
            botoes,
            text="Restaurar padrao",
            bg=self.colors["panel"],
            fg=self.colors["dim"],
            bd=0,
            padx=10,
            pady=7,
            font=("Consolas", 8),
            cursor="hand2",
            activebackground=self.colors["border"],
            command=self._restaurar
        ).pack(
            side="left",
            padx=8
        )


    def _restaurar(self):
        for var, texto in zip(
            self.vars,
            self.DEFAULTS
        ):
            var.set(texto)


    def _salvar(self):
        frases = []

        for i, var in enumerate(
            self.vars
        ):
            texto = var.get().strip()

            if not texto:
                texto = self.DEFAULTS[i]

            frases.append(texto)

        self.cfg["frases_waiting"] = frases

        self._save_config(self.cfg)

        self.comp.say(
            "Frases salvas!",
            "talking",
            2000
        )

        self.win.destroy()
