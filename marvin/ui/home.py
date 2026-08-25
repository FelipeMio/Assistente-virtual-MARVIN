import tkinter as tk

from marvin.database import db_listar
from marvin.config import load_cfg
from marvin.theme import get_palette
from .window_position import position_near
from marvin.checklist import listar_hoje


_THEME = get_palette(
    load_cfg().get(
        "tema",
        "escuro",
    )
)

BG = _THEME["win_bg"]
PANEL = _THEME["panel"]
BORDER = _THEME["border"]
TEXT = _THEME["text"]
DIM = _THEME["dim"]
ACCENT = _THEME["accent"]
GREEN = _THEME["green"]


class HomeWindow:

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
        self.comp = companion

        self.abrir_tarefas = abrir_tarefas
        self.nova_tarefa = nova_tarefa
        self.abrir_checklist = abrir_checklist
        self.abrir_resumo = abrir_resumo
        self.abrir_config = abrir_config

        self.win = tk.Toplevel(parent)

        self.win.title("MARVIN")
        self.win.geometry("620x470")
        self.win.minsize(580, 430)

        self.win.configure(bg=BG)

        self._build()
        self.refresh()

        position_near(
            self.win,
            self.comp.root,
            self.comp.W,
            self.comp.H,
        )


    def _build(self):
        topo = tk.Frame(
            self.win,
            bg=BG,
        )

        topo.pack(
            fill="x",
            padx=28,
            pady=(24, 18),
        )

        tk.Label(
            topo,
            text="MARVIN",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 22, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            topo,
            text="O que vamos fazer hoje?",
            bg=BG,
            fg=DIM,
            font=("Segoe UI", 10),
        ).pack(
            anchor="w",
            pady=(2, 0),
        )

        self.cards = tk.Frame(
            self.win,
            bg=BG,
        )

        self.cards.pack(
            fill="both",
            expand=True,
            padx=28,
        )

        self.cards.columnconfigure(
            0,
            weight=1,
        )

        self.cards.columnconfigure(
            1,
            weight=1,
        )

        self.card_tarefas = self._card(
            0,
            0,
            "Tarefas",
            "Carregando...",
            "Ver tarefas",
            self.abrir_tarefas,
        )

        self.card_checklist = self._card(
            0,
            1,
            "Checklist diário",
            "Carregando...",
            "Abrir checklist",
            self.abrir_checklist,
        )

        self.card_resumo = self._card(
            1,
            0,
            "Resumo do dia",
            "Veja o que foi feito e o que ainda falta.",
            "Ver resumo",
            self.abrir_resumo,
        )

        self.card_extensoes = self._card(
            1,
            1,
            "Extensões",
            "Carregando...",
            None,
            None,
        )

        self.ext_actions = tk.Frame(
            self.card_extensoes["frame"],
            bg=PANEL,
        )

        self.ext_actions.pack(
            anchor="w",
            fill="x",
            padx=18,
            pady=(0, 16),
        )

        rodape = tk.Frame(
            self.win,
            bg=BG,
        )

        rodape.pack(
            fill="x",
            padx=28,
            pady=(16, 22),
        )

        self._button(
            rodape,
            "+ Nova tarefa",
            self.nova_tarefa,
        ).pack(
            side="left",
        )

        self._button(
            rodape,
            "Configurações",
            self.abrir_config,
        ).pack(
            side="right",
        )


    def _card(
        self,
        row,
        column,
        titulo,
        descricao,
        botao,
        comando,
    ):
        frame = tk.Frame(
            self.cards,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        frame.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        frame.columnconfigure(
            0,
            weight=1,
        )

        tk.Label(
            frame,
            text=titulo,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 5),
        )

        label_desc = tk.Label(
            frame,
            text=descricao,
            bg=PANEL,
            fg=DIM,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=230,
        )

        label_desc.pack(
            anchor="w",
            padx=18,
            pady=(0, 12),
        )

        if botao and comando:
            self._button(
                frame,
                botao,
                comando,
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 16),
            )

        return {
            "frame": frame,
            "descricao": label_desc,
        }


    def _button(
        self,
        parent,
        texto,
        comando,
    ):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=BORDER,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            font=("Segoe UI", 9),
        )


    def refresh(self):
        try:
            pendentes = db_listar(
                apenas_pendentes=True
            )

            total_pendentes = len(
                pendentes
            )

        except Exception:
            total_pendentes = 0

        self.card_tarefas[
            "descricao"
        ].config(
            text=(
                f"{total_pendentes} tarefa(s) "
                "pendente(s)."
            )
        )

        try:
            itens = listar_hoje()

            total = len(itens)

            feitos = sum(
                1
                for item in itens
                if item["concluido"]
            )

        except Exception:
            total = 0
            feitos = 0

        self.card_checklist[
            "descricao"
        ].config(
            text=(
                f"{feitos} de {total} "
                "item(ns) concluído(s) hoje."
            )
        )

        try:
            quantidade_extensoes = len(
                getattr(
                    self.comp,
                    "_extensions",
                    [],
                )
            )

        except Exception:
            quantidade_extensoes = 0

        if quantidade_extensoes == 0:
            texto_ext = (
                "Nenhuma extensão ativa."
            )

        elif quantidade_extensoes == 1:
            texto_ext = (
                "1 extensão ativa."
            )

        else:
            texto_ext = (
                f"{quantidade_extensoes} "
                "extensões ativas."
            )

        self.card_extensoes[
            "descricao"
        ].config(
            text=texto_ext
        )

        for widget in (
            self.ext_actions.winfo_children()
        ):
            widget.destroy()

        acoes = getattr(
            self.comp,
            "_extension_actions",
            {},
        )

        if isinstance(
            acoes,
            dict,
        ):
            for nome, comando in (
                acoes.items()
            ):
                if not callable(comando):
                    continue

                self._button(
                    self.ext_actions,
                    nome,
                    comando,
                ).pack(
                    anchor="w",
                    pady=2,
                )


def abrir_home(
    parent,
    companion,
    abrir_tarefas,
    nova_tarefa,
    abrir_checklist,
    abrir_resumo,
    abrir_config,
):
    return HomeWindow(
        parent,
        companion,
        abrir_tarefas,
        nova_tarefa,
        abrir_checklist,
        abrir_resumo,
        abrir_config,
    )
