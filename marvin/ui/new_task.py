import datetime
import tkinter as tk

import customtkinter as ctk


class NewTaskWindow:

    WIDTH = 390
    HEIGHT = 590

    def __init__(
        self,
        parent,
        companion,
        prefill="",
        *,
        config,
        palette_factory,
        positioner,
        repeat_options,
        bind_auto_time,
        validate_date,
        validate_time,
        db_create,
    ):
        self.comp = companion
        self.parent = parent

        self.cfg = config

        self._palette_factory = (
            palette_factory
        )

        self._positioner = (
            positioner
        )

        self._repeat_options = tuple(
            repeat_options
        )

        self._bind_auto_time = (
            bind_auto_time
        )

        self._validate_date = (
            validate_date
        )

        self._validate_time = (
            validate_time
        )

        self._db_create = (
            db_create
        )

        self.tema = self.cfg.get(
            "tema",
            "escuro",
        )

        self.colors = self._palette_factory(self.tema, "task_form")

        ctk.set_appearance_mode(
            "Light"
            if self.tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            parent
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False,
        )

        self.win.overrideredirect(
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self.win.grab_set()

        self._drag_x = 0
        self._drag_y = 0

        self._build(
            prefill
        )

        self._positioner(
            self.win,
            self.comp
        )

        self.win.bind(
            "<Escape>",
            lambda e:
                self._close()
        )

        self.win.after(
            80,
            self._focus_title
        )


    # ========================================================
    # JANELA
    # ========================================================

    def _close(self):
        try:
            self.win.grab_release()
        except Exception:
            pass

        try:
            self.win.destroy()
        except Exception:
            pass


    def _focus_title(self):
        try:
            self.e_txt.focus()
        except Exception:
            pass


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


    # ========================================================
    # HELPERS
    # ========================================================

    def _label(
        self,
        parent,
        text,
        required=False,
    ):
        texto = text

        if required:
            texto += " *"

        label = ctk.CTkLabel(
            parent,
            text=texto.upper(),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),
        )

        label.pack(
            fill="x",
            pady=(0, 5),
        )

        return label


    def _entry(
        self,
        parent,
        variable,
        placeholder="",
    ):
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,

            height=36,

            corner_radius=7,

            fg_color=self.colors["input"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            placeholder_text=placeholder,
            placeholder_text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
        )

        entry.pack(
            fill="x",
        )

        return entry


    def _divider(
        self,
        parent,
    ):
        ctk.CTkFrame(
            parent,
            height=1,
            fg_color=self.colors["border"],
            corner_radius=0,
        ).pack(
            fill="x",
        )


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(
        self,
        prefill,
    ):
        shell = ctk.CTkFrame(
            self.win,

            fg_color=self.colors["bg"],

            corner_radius=14,

            border_width=1,
            border_color=self.colors["border"],
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1,
        )


        # ====================================================
        # TITLEBAR
        # ====================================================

        titlebar = ctk.CTkFrame(
            shell,
            height=44,
            fg_color="transparent",
        )

        titlebar.pack(
            fill="x",
        )

        titlebar.pack_propagate(
            False
        )

        titlebar.bind(
            "<ButtonPress-1>",
            self._drag_start,
        )

        titlebar.bind(
            "<B1-Motion>",
            self._drag_move,
        )


        marca = ctk.CTkFrame(
            titlebar,
            width=21,
            height=21,
            corner_radius=6,
            fg_color=self.colors["accent"],
        )

        marca.pack(
            side="left",
            padx=(14, 0),
        )

        marca.pack_propagate(
            False
        )

        ctk.CTkLabel(
            marca,
            text="",
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=9,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )


        ctk.CTkLabel(
            titlebar,
            text="NOVA TAREFA",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )


        ctk.CTkButton(
            titlebar,

            text="×",

            width=28,
            height=28,

            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["input_hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

            command=self._close,

        ).pack(
            side="right",
            padx=10,
        )


        self._divider(
            shell
        )


        # ====================================================
        # BODY
        # ====================================================

        body = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["dim"],
        )

        body.pack(
            fill="both",
            expand=True,
            padx=(20, 8),
            pady=(16, 8),
        )


        ctk.CTkLabel(
            body,

            text="Nova tarefa",

            text_color=self.colors["text"],

            anchor="w",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

        ).pack(
            fill="x",
            pady=(0, 15),
        )


        # ====================================================
        # TITULO
        # ====================================================

        self._label(
            body,
            "Título",
            True,
        )

        self.v_txt = tk.StringVar(
            value=prefill
        )

        self.e_txt = self._entry(
            body,
            self.v_txt,
            "Nome da tarefa",
        )


        # ====================================================
        # DESCRICAO
        # ====================================================

        desc_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        desc_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            desc_wrap,
            "Descrição",
        )


        self.desc_box = ctk.CTkTextbox(
            desc_wrap,

            height=76,

            corner_radius=7,

            fg_color=self.colors["input"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            wrap="word",
        )

        self.desc_box.pack(
            fill="x",
        )


        # ====================================================
        # DATA / HORA
        # ====================================================

        date_row = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        date_row.pack(
            fill="x",
            pady=(13, 0),
        )

        date_row.grid_columnconfigure(
            0,
            weight=1,
        )

        date_row.grid_columnconfigure(
            1,
            weight=1,
        )


        data_frame = ctk.CTkFrame(
            date_row,
            fg_color="transparent",
        )

        data_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
        )


        hora_frame = ctk.CTkFrame(
            date_row,
            fg_color="transparent",
        )

        hora_frame.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
        )


        self._label(
            data_frame,
            "Data",
            True,
        )

        self._label(
            hora_frame,
            "Horário",
            True,
        )


        proximo_minuto = (
            datetime.datetime.now()
            .replace(
                second=0,
                microsecond=0,
            )
            + datetime.timedelta(
                minutes=1
            )
        )


        self.v_data = tk.StringVar(
            value=(
                proximo_minuto
                .strftime(
                    "%d/%m/%Y"
                )
            )
        )

        self.v_hora = tk.StringVar(
            value=(
                proximo_minuto
                .strftime(
                    "%H:%M"
                )
            )
        )


        self.e_data = self._entry(
            data_frame,
            self.v_data,
        )

        self.e_hora = self._entry(
            hora_frame,
            self.v_hora,
        )


        self._bind_auto_time(
            self.e_hora,
            self.v_hora
        )


        self.v_data.trace_add(
            "write",
            self._validate_live
        )

        self.v_hora.trace_add(
            "write",
            self._validate_live
        )


        # ====================================================
        # REPETICAO
        # ====================================================

        repeat_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        repeat_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            repeat_wrap,
            "Repetição",
        )


        self.v_rep = tk.StringVar(
            value=self._repeat_options[0]
        )


        self.repeat_combo = ctk.CTkComboBox(
            repeat_wrap,

            variable=self.v_rep,

            values=list(
                self._repeat_options
            ),

            height=36,

            corner_radius=7,

            fg_color=self.colors["input"],
            button_color=self.colors["input"],
            button_hover_color=self.colors["input_hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            dropdown_fg_color=self.colors["card"],
            dropdown_hover_color=self.colors["input_hover"],
            dropdown_text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            dropdown_font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            state="readonly",
        )

        self.repeat_combo.pack(
            fill="x",
        )


        # ====================================================
        # PRIORIDADE
        # ====================================================

        priority_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        priority_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            priority_wrap,
            "Prioridade",
        )


        priority_row = ctk.CTkFrame(
            priority_wrap,
            fg_color="transparent",
        )

        priority_row.pack(
            fill="x",
        )

        # As tres colunas usam exatamente a mesma largura.
        for coluna in range(4):
            priority_row.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="prioridade",
            )


        self.v_prioridade = tk.StringVar(
            value="Nenhuma"
        )

        self.priority_buttons = {}


        for coluna, (texto, prioridade) in enumerate((
            ("Alta", "Alta"),
            ("Média", "Normal"),
            ("Baixa", "Baixa"),
            ("Nenhuma", "Nenhuma"),
        )):
            button = ctk.CTkButton(
                priority_row,

                text=texto,

                height=46,

                corner_radius=7,

                fg_color="transparent",

                hover_color=self.colors["input_hover"],

                border_width=1,
                border_color=self.colors["border"],

                text_color=self.colors["dim"],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),

                command=lambda p=prioridade:
                    self._set_priority(
                        p
                    ),
            )

            button.grid(
                row=0,
                column=coluna,
                sticky="ew",
                padx=(
                    (0, 3)
                    if coluna == 0
                    else (
                        (3, 0)
                        if coluna == 3
                        else (3, 3)
                    )
                ),
            )

            self.priority_buttons[
                prioridade
            ] = button


        self._set_priority(
            "Nenhuma"
        )


        # ====================================================
        # ERRO
        # ====================================================

        self.v_err = tk.StringVar()


        self.error_label = ctk.CTkLabel(
            body,

            textvariable=self.v_err,

            text_color=self.colors["error"],

            anchor="w",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        )

        self.error_label.pack(
            fill="x",
            pady=(7, 0),
        )


        # ====================================================
        # FOOTER
        # ====================================================

        footer = ctk.CTkFrame(
            shell,
            fg_color=self.colors["card"],
        )

        # O footer precisa ser reservado antes da area expansivel.
        # Reempacotamos o body depois dele para garantir que
        # Salvar/Cancelar nunca saiam da janela.
        footer.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=(4, 12),
        )

        body.pack_forget()

        body.pack(
            side="top",
            fill="both",
            expand=True,
            padx=(20, 8),
            pady=(16, 8),
        )


        ctk.CTkButton(
            footer,

            text="Salvar",

            height=36,

            corner_radius=7,

            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],

            text_color="#FFFFFF",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),

            command=self._salvar,

        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )


        ctk.CTkButton(
            footer,

            text="Cancelar",

            height=36,

            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["input_hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            command=self._close,

        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )


    # ========================================================
    # PRIORIDADE
    # ========================================================

    def _set_priority(
        self,
        prioridade,
    ):
        self.v_prioridade.set(
            prioridade
        )


        for nome, button in (
            self.priority_buttons.items()
        ):

            if nome != prioridade:
                button.configure(
                    fg_color="transparent",
                    border_color=self.colors["border"],
                    text_color=self.colors["dim"],
                )

                continue


            if nome == "Alta":
                button.configure(
                    fg_color=self.colors["high_bg"],
                    border_color=self.colors["high_fg"],
                    text_color=self.colors["high_fg"],
                )

            elif nome == "Normal":
                button.configure(
                    fg_color=self.colors["normal_bg"],
                    border_color=self.colors["normal_fg"],
                    text_color=self.colors["normal_fg"],
                )

            elif nome == "Baixa":
                button.configure(
                    fg_color=self.colors["low_bg"],
                    border_color=self.colors["low_fg"],
                    text_color=self.colors["low_fg"],
                )

            else:
                button.configure(
                    fg_color=self.colors["none_bg"],
                    border_color=self.colors["none_fg"],
                    text_color=self.colors["none_fg"],
                )


    # ========================================================
    # VALIDACAO
    # ========================================================

    def _validate_live(
        self,
        *_,
    ):
        d_ok = (
            self._validate_date(
                self.v_data.get()
            )
            is not None
        )

        h_ok = (
            self._validate_time(
                self.v_hora.get()
            )
            is not None
        )


        self.e_data.configure(
            text_color=(
                self.colors["text"]
                if d_ok
                else self.colors["error"]
            )
        )


        self.e_hora.configure(
            text_color=(
                self.colors["text"]
                if h_ok
                else self.colors["error"]
            )
        )


    # ========================================================
    # SALVAR
    # ========================================================

    def _salvar(
        self,
    ):
        txt = (
            self.v_txt
            .get()
            .strip()
        )


        desc = (
            self.desc_box
            .get(
                "1.0",
                "end"
            )
            .strip()
        )


        data = self._validate_date(
            self.v_data.get()
        )

        hora = self._validate_time(
            self.v_hora.get()
        )


        if not txt:
            self.v_err.set(
                "Título não pode ser vazio."
            )

            return


        if data is None:
            self.v_err.set(
                "Data inválida. Use DD/MM/AAAA."
            )

            return


        if hora is None:
            self.v_err.set(
                "Horário inválido. Use HH:MM."
            )

            return


        agora = datetime.datetime.now()


        try:
            task_dt = (
                datetime.datetime.strptime(
                    f"{data} {hora}",
                    "%Y-%m-%d %H:%M"
                )
            )

        except ValueError:
            self.v_err.set(
                "Data ou horário inválido."
            )

            return


        if task_dt <= agora:
            self.v_err.set(
                "Escolha um horário a partir do próximo minuto."
            )

            return


        self._db_create(
            txt,
            desc,
            data,
            hora,
            self.v_rep.get(),
            self.v_prioridade.get(),
        )


        self.comp.say(
            "Tarefa criada!",
            "talking",
            2000
        )


        self._close()
