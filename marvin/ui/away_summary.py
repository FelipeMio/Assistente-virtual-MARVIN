"""Janela "Enquanto voce estava fora"."""

import datetime

import customtkinter as ctk

from ..away import descrever_duracao
from ..quick_parse import descrever_data
from .branding import close_button, round_window, title_icon


def _fonte(size, weight="normal"):
    return ctk.CTkFont(
        family="Segoe UI",
        size=size,
        weight=weight,
    )


class AwaySummaryWindow:

    WIDTH = 390

    def __init__(
        self,
        parent,
        resumo,
        *,
        config,
        palette_factory,
        on_ver_avisos=None,
        on_ver_tarefas=None,
        on_abrir_checklist=None,
    ):
        self.resumo = resumo

        self._on_ver_avisos = on_ver_avisos
        self._on_ver_tarefas = on_ver_tarefas
        self._on_abrir_checklist = on_abrir_checklist

        tema = config.get("tema", "escuro")
        self.c = palette_factory(tema, "home")

        ctk.set_appearance_mode(
            "Light" if tema == "claro" else "Dark"
        )

        self.win = ctk.CTkToplevel(parent)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        round_window(self.win, self.c)

        self.win.minsize(self.WIDTH, 1)
        self.win.maxsize(self.WIDTH, 2000)

        self._drag = (0, 0)

        self._build()

        self.win.bind("<Escape>", lambda e: self.fechar())
        self.win.after(30, self._mostrar)

    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):
        c = self.c
        r = self.resumo

        shell = ctk.CTkFrame(
            self.win,
            fg_color=c["bg"],
            corner_radius=16,
            border_width=1,
            border_color=c["border"],
        )
        shell.pack(fill="both", expand=True, padx=1, pady=1)

        barra = ctk.CTkFrame(shell, fg_color="transparent", height=42)
        barra.pack(fill="x", padx=2, pady=(2, 0))
        barra.pack_propagate(False)

        drag = (self._drag_start, self._drag_move)

        title_icon(barra, c, drag=drag)

        rotulo = ctk.CTkLabel(
            barra,
            text="BEM-VINDO DE VOLTA",
            text_color=c["dim"],
            font=_fonte(10, "bold"),
        )
        rotulo.pack(side="left", padx=(8, 0))

        close_button(barra, c, self.fechar, hover=c["button_hover"])

        for widget in (barra, rotulo):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        corpo = ctk.CTkFrame(shell, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=18, pady=(6, 16))

        ctk.CTkLabel(
            corpo,
            text="Enquanto você estava fora",
            anchor="w",
            text_color=c["text"],
            font=_fonte(16, "bold"),
        ).pack(fill="x")

        ctk.CTkLabel(
            corpo,
            text=(
                f"Das {r.inicio.strftime('%H:%M')} às {r.fim.strftime('%H:%M')}"
                f"  ·  {descrever_duracao(r.duracao)}"
            ),
            anchor="w",
            text_color=c["dim"],
            font=_fonte(10),
        ).pack(fill="x", pady=(0, 12))

        lista = ctk.CTkFrame(corpo, fg_color="transparent")
        lista.pack(fill="x")

        for origem, qtd in sorted(r.avisos.items(), key=lambda x: -x[1]):
            self._linha(
                lista,
                qtd,
                f"{'aviso' if qtd == 1 else 'avisos'} do {origem}",
                "Chegaram nesse período",
                c["ext_bg"],
                c["ext_fg"],
                "Ver",
                self._on_ver_avisos,
            )

        if r.lembretes:
            nomes = r.lembretes[:3]
            detalhe = ", ".join(nomes)

            if len(r.lembretes) > 3:
                detalhe += f" e mais {len(r.lembretes) - 3}"

            self._linha(
                lista,
                len(r.lembretes),
                "lembrete venceu" if len(r.lembretes) == 1 else "lembretes venceram",
                detalhe,
                c["tasks_bg"],
                c["tasks_fg"],
                "Tarefas",
                self._on_ver_tarefas,
            )

        # Atrasadas de antes da ausencia (as do periodo ja
        # aparecem na linha de lembretes).
        if r.atrasadas > len(r.lembretes):
            self._linha(
                lista,
                r.atrasadas,
                "tarefa em atraso" if r.atrasadas == 1 else "tarefas em atraso",
                "Ainda abertas depois do horário",
                c["tasks_bg"],
                c["tasks_fg"],
                "Tarefas",
                self._on_ver_tarefas,
            )

        if r.checklist_pendentes:
            self._linha(
                lista,
                r.checklist_pendentes,
                (
                    "item do checklist"
                    if r.checklist_pendentes == 1
                    else "itens do checklist"
                ),
                "Ainda pendentes hoje",
                c["check_bg"],
                c["check_fg"],
                "Abrir",
                self._on_abrir_checklist,
            )

        if r.proxima:
            titulo, quando = r.proxima
            dia = descrever_data(quando.date(), r.fim.date()).lower()

            ctk.CTkLabel(
                corpo,
                text=f"Próximo: {titulo}, {dia} às {quando.strftime('%H:%M')}",
                anchor="w",
                text_color=c["dim"],
                font=_fonte(10),
            ).pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            corpo,
            text="Entendi",
            height=36,
            corner_radius=8,
            fg_color=c["accent"],
            hover_color=c["accent_hover"],
            text_color="#FFFFFF",
            font=_fonte(11, "bold"),
            command=self.fechar,
        ).pack(fill="x", pady=(14, 0))

    def _linha(self, parent, numero, texto, detalhe, bg, fg, acao, comando):
        c = self.c

        card = ctk.CTkFrame(
            parent,
            fg_color=c["card"],
            corner_radius=10,
            border_width=1,
            border_color=c["border"],
        )
        card.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            card,
            text=str(numero),
            width=40,
            height=40,
            corner_radius=10,
            fg_color=bg,
            text_color=fg,
            font=_fonte(14, "bold"),
        ).pack(side="left", padx=(10, 10), pady=10)

        if comando is not None:
            ctk.CTkButton(
                card,
                text=acao,
                width=64,
                height=28,
                corner_radius=7,
                fg_color="transparent",
                hover_color=c["button_hover"],
                border_width=1,
                border_color=c["border"],
                text_color=c["text"],
                font=_fonte(9, "bold"),
                command=lambda: self._acao(comando),
            ).pack(side="right", padx=(6, 10))

        textos = ctk.CTkFrame(card, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True, pady=8)

        ctk.CTkLabel(
            textos,
            text=texto,
            anchor="w",
            text_color=c["text"],
            font=_fonte(11, "bold"),
        ).pack(fill="x")

        ctk.CTkLabel(
            textos,
            text=detalhe,
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 190,
            text_color=c["dim"],
            font=_fonte(9),
        ).pack(fill="x")

    # ========================================================
    # ACOES
    # ========================================================

    def _acao(self, comando):
        self.fechar()

        try:
            comando()
        except Exception:
            pass

    def fechar(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def existe(self):
        try:
            return bool(self.win.winfo_exists())
        except Exception:
            return False

    # ========================================================
    # POSICAO
    # ========================================================

    def _mostrar(self):
        self.win.update_idletasks()

        largura = max(self.WIDTH, self.win.winfo_reqwidth())
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        # Topo da tela, centralizado: nao cobre os avisos
        # B2B, que aparecem ao lado do MARVIN.
        self.win.geometry(f"+{(sw - largura) // 2}+{int(sh * 0.12)}")

        # Aparece na frente, mas sem tomar o teclado de quem
        # acabou de voltar e ja esta digitando.
        self.win.deiconify()
        self.win.lift()

    def _drag_start(self, event):
        self._drag = (
            event.x_root - self.win.winfo_x(),
            event.y_root - self.win.winfo_y(),
        )

    def _drag_move(self, event):
        dx, dy = self._drag
        self.win.geometry(
            f"+{event.x_root - dx}+{event.y_root - dy}"
        )
