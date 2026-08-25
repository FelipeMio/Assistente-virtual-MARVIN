import datetime
import tkinter as tk

from marvin.ui.window_position import position_near
from marvin.config import load_cfg
from marvin.theme import get_palette

from .history import listar_dia


# ============================================================
# TEMA
# ============================================================

_THEME = get_palette(
    load_cfg().get(
        "tema",
        "escuro",
    )
)

BG = _THEME["win_bg"]
ROW = _THEME["win_bg"]
ROW_HOVER = _THEME["panel"]

TEXT = _THEME["text"]
DIM = _THEME["dim"]
DIVIDER = _THEME["border"]

RED = _THEME["red"]


def _formatar_numero(valor):
    try:
        return (
            f"{int(valor):,}"
            .replace(",", ".")
        )

    except Exception:
        return str(valor)


class GOEDashboard:

    HORA_INICIO = 8
    HORA_FIM = 19

    WIDTH = 250
    HEIGHT = 390

    def __init__(
        self,
        parent,
        companion,
    ):
        self.comp = companion

        self.win = tk.Toplevel(
            parent
        )

        self.win.title(
            "GOE hora a hora"
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False,
        )

        self.win.configure(
            bg=BG
        )

        self._build()
        self.refresh()

        position_near(
            self.win,
            companion.root,
            companion.W,
            companion.H,
        )

        self.win.after(
            30000,
            self._auto_refresh,
        )


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):
        self.lista = tk.Frame(
            self.win,
            bg=BG,
        )

        self.lista.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=16,
        )


    def _linha(
        self,
        hora,
        quantidade,
        zerado=False,
    ):
        container = tk.Frame(
            self.lista,
            bg=BG,
        )

        container.pack(
            fill="x",
        )

        linha = tk.Frame(
            container,
            bg=ROW,
            height=27,
        )

        linha.pack(
            fill="x",
        )

        linha.pack_propagate(
            False
        )

        lbl_hora = tk.Label(
            linha,
            text=f"{hora:02d}h",
            bg=ROW,
            fg=DIM,
            font=(
                "Segoe UI",
                9,
            ),
        )

        lbl_hora.pack(
            side="left",
            padx=(3, 0),
        )

        lbl_qtde = tk.Label(
            linha,
            text=quantidade,
            bg=ROW,
            fg=(
                RED
                if zerado
                else TEXT
            ),
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
        )

        lbl_qtde.pack(
            side="right",
            padx=(0, 3),
        )

        divisor = tk.Frame(
            container,
            bg=DIVIDER,
            height=1,
        )

        divisor.pack(
            fill="x",
        )

        # Hover discreto
        widgets = (
            linha,
            lbl_hora,
            lbl_qtde,
        )

        def entrar(event=None):
            for widget in widgets:
                widget.configure(
                    bg=ROW_HOVER
                )

        def sair(event=None):
            for widget in widgets:
                widget.configure(
                    bg=ROW
                )

        for widget in widgets:
            widget.bind(
                "<Enter>",
                entrar,
            )

            widget.bind(
                "<Leave>",
                sair,
            )


    # ========================================================
    # DADOS
    # ========================================================

    def refresh(self):
        hoje = (
            datetime.date.today()
        )

        leituras = listar_dia(
            hoje
        )

        por_hora = {
            int(item["hora"]):
                int(item["qtde"])
            for item in leituras
        }

        for widget in (
            self.lista
            .winfo_children()
        ):
            widget.destroy()

        for hora in range(
            self.HORA_INICIO,
            self.HORA_FIM + 1,
        ):
            qtde = por_hora.get(
                hora
            )

            if qtde is None:
                texto = "—"
                zerado = False

            else:
                texto = (
                    _formatar_numero(
                        qtde
                    )
                )

                zerado = (
                    qtde == 0
                )

            self._linha(
                hora,
                texto,
                zerado,
            )


    # ========================================================
    # ATUALIZACAO AUTOMATICA
    # ========================================================

    def _auto_refresh(self):
        try:
            if not self.win.winfo_exists():
                return

            self.refresh()

            self.win.after(
                30000,
                self._auto_refresh,
            )

        except tk.TclError:
            pass


def abrir_dashboard(
    parent,
    companion,
):
    return GOEDashboard(
        parent,
        companion,
    )