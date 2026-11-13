"""Captura rapida: cria tarefas a partir de uma frase."""

import datetime

import customtkinter as ctk

from ..quick_parse import descrever_data, interpretar
from .branding import round_window, title_icon


EXEMPLOS = (
    "reunião com o time amanhã 15h",
    "pagar boleto dia 20 prioridade alta",
    "beber água todo dia 10h",
    "ligar pro cliente sexta 9h30",
    "revisar relatório em 2 horas",
)


def _fonte(size, weight="normal"):
    return ctk.CTkFont(
        family="Segoe UI",
        size=size,
        weight=weight,
    )


class QuickCaptureWindow:

    WIDTH = 520

    def __init__(
        self,
        parent,
        companion,
        *,
        config,
        palette_factory,
        db_create,
    ):
        self.comp = companion
        self._db_create = db_create

        tema = config.get("tema", "escuro")
        self.c = palette_factory(tema, "task_form")

        ctk.set_appearance_mode(
            "Light" if tema == "claro" else "Dark"
        )

        self.win = ctk.CTkToplevel(parent)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        round_window(self.win, self.c)

        # Largura fixa: a janela nao "pula" enquanto a previa muda.
        self.win.minsize(self.WIDTH, 1)
        self.win.maxsize(self.WIDTH, 2000)

        self._resultado = None
        self._drag = (0, 0)
        self._exemplo = 0

        self._build()

        self.win.bind("<Escape>", lambda e: self.fechar())
        self.entry.bind("<Return>", lambda e: self._criar())
        self.entry.bind("<KeyRelease>", lambda e: self._atualizar())

        self._atualizar()
        self.win.after(20, self._mostrar)

    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):
        c = self.c

        shell = ctk.CTkFrame(
            self.win,
            width=self.WIDTH,
            fg_color=c["bg"],
            corner_radius=16,
            border_width=1,
            border_color=c["border"],
        )
        shell.pack(fill="both", expand=True, padx=1, pady=1)

        # Cabecalho
        topo = ctk.CTkFrame(shell, fg_color="transparent", height=40)
        topo.pack(fill="x", padx=2, pady=(2, 0))
        topo.pack_propagate(False)

        drag = (self._drag_start, self._drag_move)

        title_icon(topo, c, drag=drag)

        rotulo = ctk.CTkLabel(
            topo,
            text="CAPTURA RÁPIDA",
            text_color=c["dim"],
            font=_fonte(10, "bold"),
        )
        rotulo.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            topo,
            text="Enter cria  ·  Esc fecha",
            text_color=c["dim"],
            font=_fonte(9),
        ).pack(side="right", padx=16)

        for widget in (topo, rotulo):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        corpo = ctk.CTkFrame(shell, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        # Campo principal
        self.entry = ctk.CTkEntry(
            corpo,
            height=46,
            corner_radius=10,
            border_width=1,
            border_color=c["border"],
            fg_color=c["card"],
            text_color=c["text"],
            placeholder_text=f"Ex.: {EXEMPLOS[0]}",
            placeholder_text_color=c["dim"],
            font=_fonte(14),
        )
        self.entry.pack(fill="x")

        # Previa
        self.previa = ctk.CTkFrame(
            corpo,
            fg_color=c["card"],
            corner_radius=10,
            border_width=1,
            border_color=c["border"],
        )
        self.previa.pack(fill="x", pady=(10, 0))

        self.lbl_titulo = ctk.CTkLabel(
            self.previa,
            text="",
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 70,
            text_color=c["text"],
            font=_fonte(11, "bold"),
        )
        self.lbl_titulo.pack(fill="x", padx=14, pady=(10, 6))

        self.chips = ctk.CTkFrame(self.previa, fg_color="transparent")
        self.chips.pack(fill="x", padx=12, pady=(0, 12))

        self.lbl_erro = ctk.CTkLabel(
            corpo,
            text="",
            anchor="w",
            text_color=c["error"],
            font=_fonte(9),
        )
        self.lbl_erro.pack(fill="x", pady=(6, 0))

    def _chip(self, texto, fg, bg, destaque=True):
        ctk.CTkLabel(
            self.chips,
            text=f"  {texto}  ",
            height=22,
            corner_radius=7,
            fg_color=bg,
            text_color=fg if destaque else self.c["dim"],
            font=_fonte(9, "bold" if destaque else "normal"),
        ).pack(side="left", padx=(2, 4))

    # ========================================================
    # PREVIA
    # ========================================================

    def _atualizar(self):
        texto = self.entry.get().strip()
        c = self.c

        for widget in self.chips.winfo_children():
            widget.destroy()

        if not texto:
            self._resultado = None
            self.lbl_titulo.configure(
                text="Escreva o que precisa fazer e quando.",
                text_color=c["dim"],
                font=_fonte(11),
            )
            self.lbl_erro.configure(text="")

            for exemplo in EXEMPLOS[1:4]:
                self._chip(exemplo, c["dim"], c["surface"], destaque=False)

            return

        r = interpretar(texto)
        self._resultado = r

        self.lbl_titulo.configure(
            text=r.titulo or "…",
            text_color=c["text"] if r.titulo else c["dim"],
            font=_fonte(11, "bold"),
        )

        if r.data:
            hoje = datetime.date.today()

            self._chip(
                descrever_data(r.data, hoje),
                c["accent"],
                c["surface"],
                destaque="data" in r.detectado,
            )

            self._chip(
                f"às {r.hora}",
                c["accent"],
                c["surface"],
                destaque="hora" in r.detectado,
            )

        if r.recorrencia != "Nunca":
            self._chip(f"↻ {r.recorrencia}", c["low_fg"], c["low_bg"])

        cores_prioridade = {
            "Alta": ("high_fg", "high_bg", "Alta"),
            "Normal": ("normal_fg", "normal_bg", "Média"),
            "Baixa": ("low_fg", "low_bg", "Baixa"),
        }

        if r.prioridade in cores_prioridade:
            fg, bg, nome = cores_prioridade[r.prioridade]
            self._chip(f"Prioridade {nome}", c[fg], c[bg])

        self.lbl_erro.configure(text=r.erro)

        self.entry.configure(
            border_color=c["error"] if r.erro else c["accent"]
        )

    # ========================================================
    # ACOES
    # ========================================================

    def _criar(self):
        self._atualizar()
        r = self._resultado

        if r is None:
            return

        if not r.valida:
            self.entry.configure(border_color=self.c["error"])
            return

        self._db_create(
            r.titulo,
            "",
            r.data_iso,
            r.hora,
            r.recorrencia,
            r.prioridade,
        )

        quando = descrever_data(r.data).lower()

        try:
            self.comp.say(
                f"Anotado! {r.titulo}, {quando} às {r.hora}.",
                "talking",
                3500,
            )
        except Exception:
            pass

        self.fechar()

    def fechar(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    # ========================================================
    # POSICAO E FOCO
    # ========================================================

    def _mostrar(self):
        self.win.update_idletasks()

        largura = self.win.winfo_reqwidth()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        # Centro da tela, no terco superior (como uma busca).
        x = (sw - largura) // 2
        y = int(sh * 0.22)

        self.win.geometry(f"+{x}+{y}")
        self.win.deiconify()
        self.focar()

    def focar(self):
        try:
            self.win.lift()
            self.win.attributes("-topmost", True)
            self.win.focus_force()
            self.entry.focus_set()
        except Exception:
            pass

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

    def existe(self):
        try:
            return bool(self.win.winfo_exists())
        except Exception:
            return False
