from pathlib import Path

import customtkinter as ctk
from PIL import Image

from marvin.config import load_cfg
from marvin.theme import get_modern_palette
from marvin.database import db_listar
from marvin.checklist import listar_hoje

from .window_position import position_near



class HomeWindow:

    WIDTH = 360
    HEIGHT = 465

    def __init__(
        self,
        parent,
        companion,
        abrir_tarefas,
        nova_tarefa,
        abrir_checklist,
        abrir_resumo,
        abrir_config,
    ):
        self.parent = parent
        self.comp = companion

        self.abrir_tarefas = abrir_tarefas
        self.nova_tarefa = nova_tarefa
        self.abrir_checklist = abrir_checklist
        self.abrir_resumo = abrir_resumo
        self.abrir_config = abrir_config

        config = load_cfg()

        self.tema = config.get(
            "tema",
            "escuro",
        )

        self.colors = get_modern_palette(
            self.tema,
            "home"
        )

        ctk.set_appearance_mode(
            "Light"
            if self.tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            parent
        )

        self.win.title(
            "MARVIN"
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False,
        )

        # Remove barra nativa.
        self.win.overrideredirect(
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self._drag_x = 0
        self._drag_y = 0

        self._build()
        self.refresh()

        position_near(
            self.win,
            self.comp.root,
            self.comp.W,
            self.comp.H,
        )

        self.win.bind(
            "<FocusIn>",
            lambda event:
                self.refresh(),
        )

        self.win.after(
            80,
            self._focus,
        )


    # ========================================================
    # JANELA
    # ========================================================

    def _focus(self):
        try:
            self.win.deiconify()
            self.win.lift()
            self.win.focus_force()

        except Exception:
            pass


    def close(self):
        try:
            self.comp._home_window = None

        except Exception:
            pass

        try:
            self.win.destroy()

        except Exception:
            pass


    def _hide(self):
        try:
            self.win.withdraw()
        except Exception:
            pass


    # ========================================================
    # ARRASTAR JANELA
    # ========================================================

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.win.winfo_x()
        self._drag_y = event.y_root - self.win.winfo_y()


    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y

        self.win.geometry(
            f"+{x}+{y}"
        )


    # ========================================================
    # HELPERS VISUAIS
    # ========================================================

    def _divider(self, parent):
        return ctk.CTkFrame(
            parent,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"],
        )


    def _icon_box(
        self,
        parent,
        text,
        bg,
        fg,
    ):
        box = ctk.CTkFrame(
            parent,
            width=28,
            height=28,
            corner_radius=8,
            fg_color=bg,
        )

        box.pack_propagate(
            False
        )

        ctk.CTkLabel(
            box,
            text=text,
            text_color=fg,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        return box


    def _card(
        self,
        parent,
        row,
        column,
        icon,
        icon_bg,
        icon_fg,
        title,
        button_text,
        command,
    ):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            border_width=1,
            border_color=self.colors["border"],
            corner_radius=12,
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=4,
            pady=4,
        )

        icon_box = self._icon_box(
            card,
            icon,
            icon_bg,
            icon_fg,
        )

        icon_box.pack(
            anchor="w",
            padx=13,
            pady=(13, 7),
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold",
            ),
        )

        title_label.pack(
            fill="x",
            padx=13,
        )

        description = ctk.CTkLabel(
            card,
            text="",
            text_color=self.colors["dim"],
            anchor="w",
            justify="left",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
        )

        description.pack(
            fill="x",
            padx=13,
            pady=(2, 7),
        )

        button = ctk.CTkButton(
            card,
            text=button_text,
            width=94,
            height=27,
            corner_radius=6,

            fg_color="transparent",
            hover_color=self.colors["button_hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),

            command=command,
        )

        button.pack(
            anchor="w",
            padx=13,
            pady=(0, 12),
        )

        return {
            "frame": card,
            "description": description,
            "button": button,
        }


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["bg"],
            border_width=1,
            border_color=self.colors["border"],
            corner_radius=16,
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
            height=45,
            fg_color="transparent",
            corner_radius=0,
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


        left = ctk.CTkFrame(
            titlebar,
            fg_color="transparent",
        )

        left.pack(
            side="left",
            padx=14,
        )


        mark = ctk.CTkFrame(
            left,
            width=21,
            height=21,
            corner_radius=6,
            fg_color=self.colors["accent"],
        )

        mark.pack(
            side="left",
        )

        mark.pack_propagate(
            False
        )

        ctk.CTkLabel(
            mark,
            text="",
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )


        ctk.CTkLabel(
            left,
            text="MARVIN",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )


        close_button = ctk.CTkButton(
            titlebar,
            text="×",
            width=28,
            height=28,
            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["button_hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

            border_width=0,
            command=self.close,
        )

        close_button.pack(
            side="right",
            padx=(2, 10),
        )


        settings_button = ctk.CTkButton(
            titlebar,
            text="⚙",
            width=27,
            height=27,
            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["button_hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),

            border_width=0,
            command=self.abrir_config,
        )

        settings_button.pack(
            side="right",
            padx=2,
        )


        self._divider(
            shell
        ).pack(
            fill="x",
        )


        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            shell,
            fg_color="transparent",
            height=72,
        )

        header.pack(
            fill="x",
            padx=17,
            pady=(13, 10),
        )

        header.pack_propagate(
            False
        )


        # Cabeça do MARVIN
        icon_path = (
            Path(__file__)
            .resolve()
            .parent
            .parent
            .parent
            / "assets"
            / "marvin"
            / "marvin_head.png"
        )

        try:
            self.marvin_head_image = ctk.CTkImage(
                light_image=Image.open(
                    icon_path
                ),
                dark_image=Image.open(
                    icon_path
                ),
                size=(45, 45),
            )

            avatar = ctk.CTkLabel(
                header,
                text="",
                image=self.marvin_head_image,
                width=45,
                height=45,
            )

        except Exception:
            avatar = ctk.CTkLabel(
                header,
                text="M",
                width=40,
                height=40,
                corner_radius=10,
                fg_color=self.colors["tasks_bg"],
                text_color=self.colors["tasks_fg"],
            )

        avatar.pack(
            side="left",
        )


        greeting = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        greeting.pack(
            side="left",
            padx=(10, 0),
        )


        ctk.CTkLabel(
            greeting,
            text="Marvin",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
        ).pack(
            anchor="w",
        )


        ctk.CTkLabel(
            greeting,
            text="O que vamos fazer hoje?",
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
        ).pack(
            anchor="w",
        )


        self._divider(
            shell
        ).pack(
            fill="x",
        )


        # ====================================================
        # GRID
        # ====================================================

        grid = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        grid.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        grid.grid_columnconfigure(
            (0, 1),
            weight=1,
            uniform="cards",
        )

        grid.grid_rowconfigure(
            (0, 1),
            weight=1,
            uniform="cards",
        )


        self.card_tasks = self._card(
            grid,
            0,
            0,
            "✓",
            self.colors["tasks_bg"],
            self.colors["tasks_fg"],
            "Tarefas",
            "Ver tarefas",
            self.abrir_tarefas,
        )


        self.card_checklist = self._card(
            grid,
            0,
            1,
            "☷",
            self.colors["check_bg"],
            self.colors["check_fg"],
            "Checklist diário",
            "Abrir checklist",
            self.abrir_checklist,
        )


        self.card_summary = self._card(
            grid,
            1,
            0,
            "▥",
            self.colors["summary_bg"],
            self.colors["summary_fg"],
            "Resumo do dia",
            "Ver resumo",
            self.abrir_resumo,
        )


        # Extensões recebe tratamento diferente.
        self.card_extensions = self._card(
            grid,
            1,
            1,
            "✦",
            self.colors["ext_bg"],
            self.colors["ext_fg"],
            "Extensões",
            "",
            lambda: None,
        )

        self.card_extensions[
            "button"
        ].pack_forget()


        self.extension_buttons = ctk.CTkFrame(
            self.card_extensions["frame"],
            fg_color="transparent",
        )

        self.extension_buttons.pack(
            fill="x",
            padx=13,
            pady=(0, 12),
        )


        # ====================================================
        # FOOTER
        # ====================================================

        self._divider(
            shell
        ).pack(
            fill="x",
        )


        footer = ctk.CTkFrame(
            shell,
            height=54,
            fg_color="transparent",
        )

        footer.pack(
            fill="x",
            padx=11,
            pady=9,
        )

        footer.pack_propagate(
            False
        )


        ctk.CTkButton(
            footer,
            text="+ Nova tarefa",
            height=36,
            corner_radius=8,

            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],

            text_color="#FFFFFF",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),

            command=self.nova_tarefa,
        ).pack(
            side="left",
            fill="x",
            expand=True,
        )




    # ========================================================
    # DADOS
    # ========================================================

    def refresh(self):

        # ----------------------------------------------------
        # Tarefas
        # ----------------------------------------------------

        try:
            pendentes = db_listar(
                apenas_pendentes=True
            )

            total = len(
                pendentes
            )

        except Exception:
            total = 0


        self.card_tasks[
            "description"
        ].configure(
            text=(
                f"{total} pendente"
                if total == 1
                else f"{total} pendentes"
            )
        )


        # ----------------------------------------------------
        # CHECKLIST
        # ----------------------------------------------------

        try:
            itens = listar_hoje()

            total_itens = len(
                itens
            )

            concluidos = 0

            for item in itens:

                if isinstance(
                    item,
                    dict
                ):
                    if item.get(
                        "concluido"
                    ):
                        concluidos += 1

                elif (
                    isinstance(
                        item,
                        (list, tuple)
                    )
                    and item
                    and item[-1]
                ):
                    concluidos += 1

        except Exception:
            total_itens = 0
            concluidos = 0


        self.card_checklist[
            "description"
        ].configure(
            text=(
                f"{concluidos} de "
                f"{total_itens} concluído"
            )
        )


        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        self.card_summary[
            "description"
        ].configure(
            text="O feito e o que falta"
        )


        # ----------------------------------------------------
        # EXTENSOES
        # ----------------------------------------------------

        quantidade = len(
            getattr(
                self.comp,
                "_extensions",
                [],
            )
        )


        self.card_extensions[
            "description"
        ].configure(
            text=(
                "1 ativa"
                if quantidade == 1
                else f"{quantidade} ativas"
            )
        )


        for widget in (
            self.extension_buttons
            .winfo_children()
        ):
            widget.destroy()


        actions = getattr(
            self.comp,
            "_extension_actions",
            {},
        )

        if not isinstance(
            actions,
            dict
        ):
            return


        for nome, comando in actions.items():

            if not callable(
                comando
            ):
                continue


            ctk.CTkButton(
                self.extension_buttons,

                text=nome,

                height=24,

                corner_radius=5,

                fg_color=self.colors["ext_bg"],
                hover_color=self.colors["accent"],

                text_color=self.colors["ext_fg"],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                    weight="bold",
                ),

                command=comando,

            ).pack(
                anchor="w",
            )


# ============================================================
# ABRIR CENTRAL
# ============================================================

def abrir_home(
    parent,
    companion,
    abrir_tarefas,
    nova_tarefa,
    abrir_checklist,
    abrir_resumo,
    abrir_config,
):

    existente = getattr(
        companion,
        "_home_window",
        None,
    )


    if (
        existente is not None
        and existente.win.winfo_exists()
    ):
        existente.win.deiconify()

        existente.refresh()

        existente.win.lift()
        existente.win.focus_force()

        return existente


    janela = HomeWindow(
        parent,
        companion,
        abrir_tarefas,
        nova_tarefa,
        abrir_checklist,
        abrir_resumo,
        abrir_config,
    )


    companion._home_window = janela

    return janela