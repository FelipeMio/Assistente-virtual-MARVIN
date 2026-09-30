import datetime
import tkinter as tk

import customtkinter as ctk

from tkinter import messagebox


class TaskWindow:

    WIDTH = 470
    HEIGHT = 610

    def __init__(
        self,
        parent,
        companion,
        *,
        config,
        palette_factory,
        positioner,
        new_task_factory,
        edit_task_factory,
        db_list_prioritized,
        db_list,
        db_complete,
        db_uncomplete,
        db_delete,
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

        self._new_task_factory = (
            new_task_factory
        )

        self._edit_task_factory = (
            edit_task_factory
        )

        self._db_list_prioritized = (
            db_list_prioritized
        )

        self._db_list = (
            db_list
        )

        self._db_complete = (
            db_complete
        )

        self._db_uncomplete = (
            db_uncomplete
        )

        self._db_delete = (
            db_delete
        )

        self.tema = self.cfg.get(
            "tema",
            "escuro"
        )

        self.colors = self._palette_factory(self.tema, "task_list")

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
            True,
            True
        )

        self.win.minsize(
            430,
            500
        )

        self.win.overrideredirect(
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self._drag_x = 0
        self._drag_y = 0

        self.filtro = tk.StringVar(
            value="todas"
        )

        self.filtro_prioridade = tk.StringVar(
            value="todas"
        )

        self.busca = tk.StringVar(
            value=""
        )

        self.status_buttons = {}
        self.priority_buttons = {}

        # Controle de atualizacoes da lista.
        # Evita reconstrucoes repetidas causadas por foco
        # e por digitacao rapida na busca.
        self._refresh_job = None
        self._window_has_focus = False

        self._build()

        self._positioner(
            self.win,
            self.comp
        )

        self.win.bind(
            "<Escape>",
            lambda e: self.win.destroy()
        )

        self.win.bind(
            "<FocusIn>",
            self._on_focus_in
        )

        self.win.bind(
            "<FocusOut>",
            self._on_focus_out
        )


    # ========================================================
    # JANELA
    # ========================================================

    def _drag_start(self, event):
        self._drag_x = (
            event.x_root
            - self.win.winfo_x()
        )

        self._drag_y = (
            event.y_root
            - self.win.winfo_y()
        )


    def _drag_move(self, event):
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
    # CONTROLE DE REFRESH
    # ========================================================

    def _schedule_refresh(
        self,
        delay=140,
    ):
        """
        Agenda apenas um refresh.

        Se outro pedido chegar antes do tempo,
        substitui o anterior.
        """
        try:
            if not self.win.winfo_exists():
                return
        except Exception:
            return

        if self._refresh_job is not None:
            try:
                self.win.after_cancel(
                    self._refresh_job
                )
            except Exception:
                pass

        self._refresh_job = self.win.after(
            delay,
            self._run_scheduled_refresh,
        )


    def _run_scheduled_refresh(self):
        self._refresh_job = None
        self._refresh()


    def _on_focus_in(
        self,
        event,
    ):
        # FocusIn tambem e propagado quando o foco
        # passa entre controles internos da janela.
        #
        # Atualizamos apenas quando a TaskWindow
        # estava realmente sem foco antes.
        if self._window_has_focus:
            return

        try:
            if (
                event.widget.winfo_toplevel()
                is not self.win
            ):
                return
        except Exception:
            return

        self._window_has_focus = True

        # Pequeno atraso permite que a troca de
        # janela/foco termine antes da atualizacao.
        self._schedule_refresh(
            80
        )


    def _on_focus_out(
        self,
        event,
    ):
        # Espera o Tk concluir a mudanca de foco.
        # Assim, mover o foco entre dois controles
        # da propria TaskWindow nao conta como sair.
        try:
            self.win.after_idle(
                self._sync_focus_state
            )
        except Exception:
            pass


    def _sync_focus_state(self):
        try:
            foco = self.win.focus_get()

            if (
                foco is None
                or foco.winfo_toplevel()
                is not self.win
            ):
                self._window_has_focus = False

        except Exception:
            self._window_has_focus = False


    # ========================================================
    # BOTAO DE FILTRO
    # ========================================================

    def _filter_button(
        self,
        parent,
        texto,
        valor,
        var,
        grupo,
        coluna,
    ):
        b = ctk.CTkButton(
            parent,

            text=texto,

            height=34,

            corner_radius=8,

            fg_color="transparent",
            hover_color=self.colors["hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),

            command=lambda: self._set_filter(
                var,
                valor,
                grupo
            ),
        )

        b.grid(
            row=0,
            column=coluna,
            sticky="ew",
            padx=3,
        )

        grupo[valor] = b

        return b


    def _set_filter(
        self,
        var,
        valor,
        grupo,
    ):
        var.set(
            valor
        )

        for chave, button in grupo.items():

            selecionado = (
                chave == valor
            )

            button.configure(
                fg_color=(
                    self.colors["hover"]
                    if selecionado
                    else "transparent"
                ),

                border_color=(
                    self.colors["accent"]
                    if selecionado
                    else self.colors["border"]
                ),

                text_color=(
                    self.colors["accent"]
                    if selecionado
                    else self.colors["text"]
                ),
            )

        self._refresh()


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):

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
            fill="x"
        )

        titlebar.pack_propagate(
            False
        )

        titlebar.bind(
            "<ButtonPress-1>",
            self._drag_start
        )

        titlebar.bind(
            "<B1-Motion>",
            self._drag_move
        )


        ctk.CTkLabel(
            titlebar,

            text="MARVIN — TAREFAS",

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),

        ).pack(
            side="left",
            padx=16,
        )


        ctk.CTkButton(
            titlebar,

            text="×",

            width=28,
            height=28,

            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

            command=self.win.destroy,

        ).pack(
            side="right",
            padx=10,
        )


        ctk.CTkFrame(
            shell,
            height=1,
            fg_color=self.colors["border"],
        ).pack(
            fill="x"
        )


        # ====================================================
        # CORPO
        # ====================================================

        body = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(16, 14),
        )


        # ====================================================
        # TITULO + NOVA
        # ====================================================

        header = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
            pady=(0, 16),
        )


        ctk.CTkLabel(
            header,

            text="Tarefas",

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

        ).pack(
            side="left"
        )


        ctk.CTkButton(
            header,

            text="+ Nova",

            width=68,
            height=30,

            corner_radius=8,

            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],

            text_color="#FFFFFF",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),

            command=lambda:
                self._new_task_factory(
                    self.win,
                    self.comp
                ),

        ).pack(
            side="right"
        )


        # ====================================================
        # STATUS
        # ====================================================

        status_line = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        status_line.pack(
            fill="x",
            pady=(0, 7),
        )


        ctk.CTkLabel(
            status_line,

            text="STATUS",

            width=68,

            anchor="w",

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            side="left"
        )


        status_buttons = ctk.CTkFrame(
            status_line,
            fg_color="transparent",
        )

        status_buttons.pack(
            side="left",
            fill="x",
            expand=True,
        )

        for coluna in range(3):
            status_buttons.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="status",
            )

        for coluna, (texto, valor) in enumerate((
            ("Todas", "todas"),
            ("Pendentes", "pendentes"),
            ("Concluídas", "concluidas"),
        )):
            self._filter_button(
                status_buttons,
                texto,
                valor,
                self.filtro,
                self.status_buttons,
                coluna,
            )


        # ====================================================
        # PRIORIDADE
        # ====================================================

        priority_line = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        priority_line.pack(
            fill="x",
            pady=(0, 12),
        )


        ctk.CTkLabel(
            priority_line,

            text="PRIORIDADE",

            width=68,

            anchor="w",

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            side="left"
        )


        priority_buttons = ctk.CTkFrame(
            priority_line,
            fg_color="transparent",
        )

        priority_buttons.pack(
            side="left",
            fill="x",
            expand=True,
        )

        for coluna in range(5):
            priority_buttons.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="prioridade",
            )

        for coluna, (texto, valor) in enumerate((
            ("Todas", "todas"),
            ("Alta", "Alta"),
            ("Média", "Normal"),
            ("Baixa", "Baixa"),
            ("Nenhuma", "Nenhuma"),
        )):
            self._filter_button(
                priority_buttons,
                texto,
                valor,
                self.filtro_prioridade,
                self.priority_buttons,
                coluna,
            )


        self._set_filter(
            self.filtro,
            "todas",
            self.status_buttons,
        )

        self._set_filter(
            self.filtro_prioridade,
            "todas",
            self.priority_buttons,
        )


        # ====================================================
        # BUSCA
        # ====================================================

        self.search_entry = ctk.CTkEntry(
            body,

            textvariable=self.busca,

            height=36,

            corner_radius=8,

            fg_color=self.colors["card"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            placeholder_text="Buscar tarefa...",
            placeholder_text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
        )

        self.search_entry.pack(
            fill="x",
            pady=(0, 13),
        )


        self.busca.trace_add(
            "write",
            lambda *_:
                self._schedule_refresh(
                    160
                )
        )


        ctk.CTkFrame(
            body,
            height=1,
            fg_color=self.colors["border"],
        ).pack(
            fill="x",
            pady=(0, 7),
        )


        # ====================================================
        # LISTA
        # ====================================================

        self.lf = ctk.CTkScrollableFrame(
            body,

            fg_color="transparent",

            scrollbar_button_color=
                self.colors["border"],

            scrollbar_button_hover_color=
                self.colors["dim"],
        )

        self.lf.pack(
            fill="both",
            expand=True,
        )


        self._refresh()


    # ========================================================
    # REFRESH
    # ========================================================

    def _refresh(self):

        if not hasattr(
            self,
            "lf"
        ):
            return

        # Um refresh imediato, por exemplo apos
        # clicar em um filtro, invalida qualquer
        # refresh que ainda estivesse aguardando.
        if self._refresh_job is not None:
            try:
                self.win.after_cancel(
                    self._refresh_job
                )
            except Exception:
                pass

            self._refresh_job = None


        for widget in (
            self.lf.winfo_children()
        ):
            widget.destroy()


        rows = self._db_list_prioritized()


        filtro_status = (
            self.filtro.get()
        )

        filtro_prioridade = (
            self.filtro_prioridade.get()
        )

        busca = (
            self.busca
            .get()
            .strip()
            .lower()
        )


        filtradas = []


        for row in rows:

            tid = row[0]
            texto = str(
                row[1] or ""
            )

            desc = str(
                row[2] or ""
            )

            concluida = bool(
                row[6]
            )

            prioridade = (
                row[8]
                or "Normal"
            )


            if (
                filtro_status
                == "pendentes"
                and concluida
            ):
                continue


            if (
                filtro_status
                == "concluidas"
                and not concluida
            ):
                continue


            if (
                filtro_prioridade
                != "todas"
                and prioridade
                != filtro_prioridade
            ):
                continue


            if (
                busca
                and busca
                not in (
                    texto
                    + " "
                    + desc
                ).lower()
            ):
                continue


            filtradas.append(
                row
            )


        pending = [
            row
            for row in filtradas
            if not row[6]
        ]


        done = [
            row
            for row in filtradas
            if row[6]
        ]


        if (
            filtro_status
            in ("todas", "pendentes")
            and pending
        ):
            self._section(
                "PENDENTES",
                pending
            )


        if (
            filtro_status
            in ("todas", "concluidas")
            and done
        ):
            self._section(
                "CONCLUÍDAS",
                done
            )


        if not pending and not done:
            ctk.CTkLabel(
                self.lf,

                text="Nenhuma tarefa encontrada.",

                text_color=self.colors["dim"],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                ),

            ).pack(
                pady=30
            )


    # ========================================================
    # SECAO
    # ========================================================

    def _section(
        self,
        titulo,
        rows,
    ):

        head = ctk.CTkFrame(
            self.lf,
            fg_color="transparent",
        )

        head.pack(
            fill="x",
            pady=(8, 5),
        )


        ctk.CTkLabel(
            head,

            text=titulo,

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            side="left"
        )


        ctk.CTkLabel(
            head,

            text=str(
                len(rows)
            ),

            width=25,
            height=20,

            corner_radius=10,

            fg_color=self.colors["hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),

        ).pack(
            side="left",
            padx=(7, 0),
        )


        for row in rows:
            self._row(
                row
            )


    # ========================================================
    # TAREFA
    # ========================================================

    def _row(
        self,
        row,
    ):

        (
            tid,
            texto,
            desc,
            data,
            hora,
            rep,
            concluida,
            lembrado,
            prioridade,
        ) = row

        prioridade = (
            prioridade
            or "Normal"
        )


        task = ctk.CTkFrame(
            self.lf,

            fg_color=self.colors["card"],

            corner_radius=10,

            border_width=1,
            border_color=self.colors["border"],
        )

        task.pack(
            fill="x",
            padx=2,
            pady=(0, 8),
        )


        # ----------------------------------------------------
        # CHECK
        # ----------------------------------------------------

        check = ctk.CTkButton(
            task,

            text="✓" if concluida else "",

            width=21,
            height=21,

            corner_radius=11,

            fg_color=(
                self.colors["done_bg"]
                if concluida
                else "transparent"
            ),

            hover_color=self.colors[
                "done_bg"
            ],

            border_width=1,

            border_color=(
                self.colors["done_fg"]
                if concluida
                else self.colors["border"]
            ),

            text_color=self.colors[
                "done_fg"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),

            command=lambda i=tid:
                self._toggle_done(i),
        )

        check.pack(
            side="left",
            anchor="center",
            padx=(12, 9),
        )


        # ----------------------------------------------------
        # TEXTO
        # ----------------------------------------------------

        center = ctk.CTkFrame(
            task,
            fg_color="transparent",
        )

        center.pack(
            side="left",
            fill="both",
            expand=True,
            pady=5,
        )


        titulo = ctk.CTkLabel(
            center,

            text=texto,

            text_color=(
                self.colors["dim"]
                if concluida
                else self.colors["text"]
            ),

            anchor="w",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight=(
                    "normal"
                    if concluida
                    else "bold"
                ),
            ),
        )

        titulo.pack(
            fill="x"
        )


        if desc.strip():
            ctk.CTkLabel(
                center,

                text=desc.strip(),

                text_color=self.colors["dim"],

                anchor="w",
                justify="left",

                wraplength=300,

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                ),
            ).pack(
                fill="x",
                pady=(2, 3),
            )


        meta = ctk.CTkFrame(
            center,
            fg_color="transparent",
        )

        meta.pack(
            fill="x",
            pady=(3, 0),
        )


        if prioridade == "Alta":
            p_bg = self.colors["high_bg"]
            p_fg = self.colors["high_fg"]
            p_text = "Alta"

        elif prioridade == "Normal":
            p_bg = self.colors["medium_bg"]
            p_fg = self.colors["medium_fg"]
            p_text = "Média"

        elif prioridade == "Baixa":
            p_bg = self.colors["low_bg"]
            p_fg = self.colors["low_fg"]
            p_text = "Baixa"

        else:
            p_bg = self.colors["none_bg"]
            p_fg = self.colors["none_fg"]
            p_text = "Nenhuma"


        ctk.CTkLabel(
            meta,

            text=p_text,

            height=19,

            corner_radius=6,

            fg_color=p_bg,

            text_color=p_fg,

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
                weight="bold",
            ),

        ).pack(
            side="left"
        )


        try:
            data_br = (
                datetime.datetime
                .strptime(
                    data,
                    "%Y-%m-%d"
                )
                .strftime(
                    "%d/%m/%y"
                )
            )

        except Exception:
            data_br = data


        ctk.CTkLabel(
            meta,

            text=f"{data_br} · {hora[:5]}",

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

        ).pack(
            side="left",
            padx=(7, 0),
        )


        # ----------------------------------------------------
        # ACOES
        # ----------------------------------------------------

        actions = ctk.CTkFrame(
            task,
            fg_color="transparent",
        )

        actions.pack(
            side="right",
            anchor="n",
            pady=6,
        )


        ctk.CTkButton(
            actions,

            text="Editar",

            width=62,
            height=30,

            fg_color="transparent",
            hover_color=self.colors["hover"],

            text_color=self.colors["accent"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

            command=lambda i=tid:
                self._edit_task_factory(
                    self.win,
                    self.comp,
                    i,
                    self._refresh
                ),
        ).pack(
            side="left"
        )


        ctk.CTkButton(
            actions,

            text="Excluir",

            width=62,
            height=30,

            fg_color="transparent",
            hover_color=self.colors["hover"],

            text_color=self.colors["red"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

            command=lambda i=tid:
                self._delete(i),
        ).pack(
            side="left"
        )


        ctk.CTkFrame(
            self.lf,

            height=1,

            fg_color=self.colors["border"],

        ).pack(
            fill="x",
            pady=(2, 3),
        )


    # ========================================================
    # CONCLUIR / DESCONCLUIR
    # ========================================================

    def _toggle_done(
        self,
        tid,
    ):

        for row in self._db_list():

            if row[0] != tid:
                continue


            if row[6]:
                self._db_uncomplete(
                    tid
                )

            else:
                self._db_complete(
                    tid
                )

            break


        self._refresh()


        self.comp.say(
            "Tarefa atualizada!",
            "talking",
            2000
        )


    # ========================================================
    # EXCLUIR
    # ========================================================

    def _delete(
        self,
        tid,
    ):

        if messagebox.askyesno(
            "MARVIN",
            "Excluir esta tarefa?",
            parent=self.win,
        ):
            self._db_delete(
                tid
            )

            self._refresh()
