import datetime
import sys
import time
import tkinter as tk

import customtkinter as ctk

from pathlib import Path
from tkinter import messagebox

from PIL import Image

from ..config import load_cfg
from ..database import (
    db_listar,
    db_streak_hoje,
)
from ..theme import get_modern_palette


# ============================================================
# WIN32
# Mantem a mesma logica de monitor usada pelo painel original.
# ============================================================

ctypes = None
wintypes = None
MONITORINFO = None


if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes

    except ImportError:
        pass

    else:
        class MONITORINFO(
            ctypes.Structure
        ):
            _fields_ = [
                (
                    "cbSize",
                    wintypes.DWORD,
                ),
                (
                    "rcMonitor",
                    wintypes.RECT,
                ),
                (
                    "rcWork",
                    wintypes.RECT,
                ),
                (
                    "dwFlags",
                    wintypes.DWORD,
                ),
            ]


class InteractionPanel:

    WIDTH = 210

    def __init__(
        self,
        root,
        companion,
        mode="idle",
        *,
        settings_factory,
        task_factory,
        new_task_factory,
        snooze_factory,
    ):
        self.comp = companion
        self.root = root
        self.mode = mode

        self._settings_factory = (
            settings_factory
        )

        self._task_factory = (
            task_factory
        )

        self._new_task_factory = (
            new_task_factory
        )

        self._snooze_factory = (
            snooze_factory
        )

        self.tema = load_cfg().get(
            "tema",
            "escuro",
        )

        self.colors = get_modern_palette(self.tema, "interaction")

        ctk.set_appearance_mode(
            "Light"
            if self.tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            root
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

        self.shell = ctk.CTkFrame(
            self.win,

            width=self.WIDTH,

            fg_color=self.colors["bg"],

            corner_radius=14,

            border_width=1,
            border_color=self.colors["border"],
        )

        self.shell.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1,
        )

        if mode == "alert":
            self._build_alert(
                self.shell
            )
        else:
            self._build_idle(
                self.shell
            )

        self._position()

        # Nao fecha imediatamente quando o clique
        # em um botao altera o foco.
        self.win.bind(
            "<FocusOut>",
            self._on_focus_out
        )

        self.win.bind(
            "<Escape>",
            lambda e:
                self._close()
        )

        self.win.focus_force()


    # ========================================================
    # POSICIONAMENTO
    # ========================================================

    def _position(self):
        root = self.root

        self.win.update_idletasks()

        ww = self.win.winfo_reqwidth()
        wh = self.win.winfo_reqheight()

        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = self.comp.W

        mon_left = 0
        mon_top = 0
        mon_right = root.winfo_screenwidth()
        mon_bottom = root.winfo_screenheight()

        if sys.platform == "win32":
            try:


                user32 = (
                    ctypes.windll.user32
                )

                monitor = (
                    user32.MonitorFromWindow(
                        root.winfo_id(),
                        2
                    )
                )

                info = MONITORINFO()
                info.cbSize = (
                    ctypes.sizeof(
                        MONITORINFO
                    )
                )

                if user32.GetMonitorInfoW(
                    monitor,
                    ctypes.byref(info)
                ):
                    mon_left = (
                        info.rcWork.left
                    )

                    mon_top = (
                        info.rcWork.top
                    )

                    mon_right = (
                        info.rcWork.right
                    )

                    mon_bottom = (
                        info.rcWork.bottom
                    )

            except Exception:
                pass

        gap = 8

        if (
            rx - ww - gap
            >= mon_left
        ):
            px = (
                rx
                - ww
                - gap
            )

        elif (
            rx
            + rw
            + gap
            + ww
            <= mon_right
        ):
            px = (
                rx
                + rw
                + gap
            )

        else:
            px = max(
                mon_left,
                min(
                    rx + rw + gap,
                    mon_right - ww
                )
            )

        py = max(
            mon_top,
            min(
                ry + 15,
                mon_bottom - wh
            )
        )

        self.win.geometry(
            f"+{px}+{py}"
        )


    # ========================================================
    # FECHAMENTO / FOCO
    # ========================================================

    def _on_focus_out(
        self,
        event=None,
    ):
        try:
            self.win.after(
                50,
                self._check_focus_out
            )

        except Exception:
            pass


    def _check_focus_out(self):
        try:
            if not self.win.winfo_exists():
                return

            mouse_x = (
                self.win.winfo_pointerx()
            )

            mouse_y = (
                self.win.winfo_pointery()
            )

            x = (
                self.win.winfo_rootx()
            )

            y = (
                self.win.winfo_rooty()
            )

            largura = (
                self.win.winfo_width()
            )

            altura = (
                self.win.winfo_height()
            )

            mouse_dentro = (
                x
                <= mouse_x
                <= x + largura

                and

                y
                <= mouse_y
                <= y + altura
            )

            if mouse_dentro:
                return

            foco = (
                self.win.focus_get()
            )

            if foco is not None:
                try:
                    if (
                        foco.winfo_toplevel()
                        == self.win
                    ):
                        return

                except Exception:
                    pass

            self._close()

        except tk.TclError:
            pass

        except Exception:
            pass


    def _close(self):
        try:
            self.win.destroy()

        except Exception:
            pass


    # ========================================================
    # HEADER
    # ========================================================

    def _header(
        self,
        parent,
        actions=False,
    ):

        header = ctk.CTkFrame(
            parent,
            height=49,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
        )

        header.pack_propagate(
            False
        )


        # ----------------------------------------------------
        # MARVIN
        # ----------------------------------------------------

        icon_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "assets"
            / "marvin"
            / "marvin_head.png"
        )

        try:
            self.header_marvin_image = ctk.CTkImage(
                light_image=Image.open(
                    icon_path
                ),
                dark_image=Image.open(
                    icon_path
                ),
                size=(30, 30),
            )

            ctk.CTkLabel(
                header,
                text="",
                image=self.header_marvin_image,
                width=30,
                height=30,
            ).pack(
                side="left",
                padx=(12, 0),
            )

        except Exception:
            ctk.CTkLabel(
                header,
                text="M",
                width=28,
                height=28,
                corner_radius=7,
                fg_color=self.colors["accent"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
            ).pack(
                side="left",
                padx=(12, 0),
            )


        ctk.CTkLabel(
            header,

            text="MARVIN",

            text_color=self.colors[
                "text"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),

        ).pack(
            side="left",
            padx=(8, 0),
        )


        # ----------------------------------------------------
        # CONTROLES DO CABECALHO
        # ----------------------------------------------------

        if actions:

            ctk.CTkButton(
                header,

                text="×",

                width=30,
                height=30,

                corner_radius=7,

                fg_color="transparent",

                hover_color=self.colors[
                    "orange_bg"
                ],

                text_color=self.colors[
                    "dim"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=18,
                ),

                command=lambda: (
                    [
                        self._close(),
                        self.comp._on_close(),
                    ]
                    if messagebox.askyesno(
                        "Fechar MARVIN",
                        "Deseja realmente fechar o MARVIN?",
                        parent=self.win,
                    )
                    else None
                ),

            ).pack(
                side="right",
                padx=(2, 8),
            )


            ctk.CTkButton(
                header,

                text="⚙",

                width=30,
                height=30,

                corner_radius=7,

                fg_color="transparent",

                hover_color=self.colors[
                    "hover"
                ],

                text_color=self.colors[
                    "dim"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI Symbol",
                    size=16,
                ),

                command=lambda: [
                    self._close(),
                    self._settings_factory(
                        self.root,
                        self.comp
                    ),
                ],

            ).pack(
                side="right",
                padx=2,
                pady=(3, 0),
            )


        ctk.CTkFrame(
            parent,

            height=1,

            corner_radius=0,

            fg_color=self.colors[
                "border"
            ],

        ).pack(
            fill="x",
            padx=14,
        )




    # ========================================================
    # BOTAO
    # ========================================================

    def _button(
        self,
        parent,
        text,
        command,
        accent=False,
    ):

        if accent:
            fg = self.colors[
                "accent"
            ]

            hover = self.colors[
                "accent_hover"
            ]

            text_color = "#FFFFFF"

            border_width = 0

        else:
            fg = "transparent"

            hover = self.colors[
                "hover"
            ]

            text_color = self.colors[
                "text"
            ]

            border_width = 1


        button = ctk.CTkButton(
            parent,

            text=text,

            height=32,

            corner_radius=7,

            fg_color=fg,

            hover_color=hover,

            text_color=text_color,

            border_width=border_width,
            border_color=self.colors[
                "border"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),

            command=command,
        )

        button.pack(
            fill="x",
            padx=14,
            pady=3,
        )

        return button


    # ========================================================
    # MODO NORMAL
    # ========================================================

    def _build_idle(
        self,
        parent,
    ):

        self._header(
            parent,
            actions=True,
        )


        rows = db_listar()


        n = len([
            r
            for r in rows
            if not r[6]
        ])


        hoje = (
            datetime.date.today()
            .isoformat()
        )


        n_hoje = len([
            r
            for r in rows
            if (
                not r[6]
                and r[3] == hoje
            )
        ])


        streak = (
            db_streak_hoje()
        )


        # ====================================================
        # RESUMO
        # ====================================================

        body = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        body.pack(
            fill="x",
            padx=14,
            pady=(17, 14),
        )


        if n == 0:
            mensagem = (
                "Nenhuma tarefa pendente."
            )

        elif n == 1:
            mensagem = (
                "1 tarefa pendente."
            )

        else:
            mensagem = (
                f"{n} tarefas pendentes."
            )


        ctk.CTkLabel(
            body,

            text=mensagem,

            text_color=self.colors[
                "text"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

        ).pack()


        # ----------------------------------------------------
        # ESTATISTICAS NA MESMA LINHA
        # ----------------------------------------------------

        stats = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        stats.pack(
            pady=(7, 0),
        )


        hoje_texto = (
            "1 para hoje."
            if n_hoje == 1
            else
            f"{n_hoje} para hoje."
        )


        ctk.CTkLabel(
            stats,

            text=hoje_texto,

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

        ).pack(
            side="left",
        )


        if streak:

            streak_texto = (
                "1 concluída hoje"
                if streak == 1
                else
                f"{streak} concluídas hoje"
            )


            ctk.CTkLabel(
                stats,

                text=streak_texto,

                text_color=self.colors[
                    "green"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),

            ).pack(
                side="left",
                padx=(12, 0),
            )


        # ====================================================
        # CENTRAL
        # ====================================================

        self._button(
            parent,

            "Central do MARVIN",

            lambda: [
                self._close(),
                self.comp._open_home()
            ],
        )


        # ====================================================
        # TAREFAS + NOVA TAREFA
        # ====================================================

        task_actions = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        task_actions.pack(
            fill="x",
            padx=14,
            pady=3,
        )

        task_actions.grid_columnconfigure(
            0,
            weight=1,
            uniform="task_actions",
        )

        task_actions.grid_columnconfigure(
            1,
            weight=1,
            uniform="task_actions",
        )


        ctk.CTkButton(
            task_actions,

            text="Ver tarefas",

            width=1,
            height=32,

            corner_radius=7,

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

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

            command=lambda: [
                self._close(),
                self._task_factory(
                    self.root,
                    self.comp
                )
            ],

        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 3),
        )


        ctk.CTkButton(
            task_actions,

            text="+ Nova tarefa",

            width=1,
            height=32,

            corner_radius=7,

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

            command=lambda: [
                self._close(),
                self._new_task_factory(
                    self.root,
                    self.comp
                )
            ],

        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(3, 0),
        )


        # ====================================================
        # MODO COMPACTO
        # ====================================================

        self._button(
            parent,

            self.comp._np_label(),

            lambda: [
                self._close(),
                self.comp._toggle_np()
            ],
        )


        # ====================================================
        # AGORA NAO
        # ====================================================

        agora_nao = ctk.CTkButton(
            parent,

            text="Agora não",

            height=27,

            corner_radius=6,

            fg_color="transparent",

            hover_color=self.colors[
                "hover"
            ],

            text_color=self.colors[
                "dim"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),

            command=self._close,
        )


        agora_nao.pack(
            fill="x",
            padx=14,
            pady=(4, 11),
        )




    # ========================================================
    # MODO ALERTA
    # ========================================================

    def _build_alert(
        self,
        parent,
    ):

        self._header(
            parent
        )


        reminder_queue = (
            self.comp
            ._reminder_queue
        )

        task = (
            reminder_queue[0]
            if reminder_queue
            else None
        )

        name = (
            task[1]
            if task
            else "tarefa"
        )

        hora = (
            task[4][:5]
            if task
            else ""
        )


        body = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        body.pack(
            fill="x",
            padx=14,
            pady=(14, 10),
        )


        icon = ctk.CTkFrame(
            body,

            width=34,
            height=34,

            corner_radius=17,

            fg_color=self.colors[
                "orange_bg"
            ],

            border_width=1,
            border_color=self.colors[
                "accent"
            ],
        )

        icon.pack()

        icon.pack_propagate(
            False
        )


        ctk.CTkLabel(
            icon,

            text="!",

            text_color=self.colors[
                "accent"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),

        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )


        ctk.CTkLabel(
            body,

            text=(
                f"Lembrete · {hora}"
                if hora
                else "Lembrete"
            ),

            text_color=self.colors[
                "accent"
            ],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),

        ).pack(
            pady=(8, 3),
        )


        ctk.CTkLabel(
            body,

            text=name,

            text_color=self.colors[
                "text"
            ],

            wraplength=190,

            justify="center",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),

        ).pack()


        n_fila = len(
            reminder_queue
        )


        if n_fila > 1:
            restantes = n_fila - 1

            fila_texto = (
                f"+1 lembrete na fila"
                if restantes == 1
                else
                f"+{restantes} lembretes na fila"
            )

            ctk.CTkLabel(
                body,

                text=fila_texto,

                text_color=self.colors[
                    "dim"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),

            ).pack(
                pady=(4, 0),
            )


        self._button(
            parent,

            "Concluir",

            lambda: [
                self._close(),
                self.comp.complete_task()
            ],

            accent=True,
        )


        self._button(
            parent,

            "Adiar",

            lambda: [
                self._close(),
                self._snooze_factory(
                    self.root,
                    self.comp,
                    task
                )
            ],
        )


        self._button(
            parent,

            "Ver tarefas",

            lambda: [
                self._close(),
                self._task_factory(
                    self.root,
                    self.comp
                )
            ],
        )


        ctk.CTkFrame(
            parent,
            height=7,
            fg_color="transparent",
        ).pack()
