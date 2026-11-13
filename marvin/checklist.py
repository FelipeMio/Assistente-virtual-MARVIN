import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from .config import load_cfg
from .database import DB_F
from .theme import get_modern_palette
from .ui.branding import close_button, title_icon, title_text
from .ui.window_position import position_near


FREQUENCIAS = (
    "Todo dia",
    "Seg a Sex",
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo",
    "Seg/Qua/Sex",
    "Ter/Qui",
    "Fins de semana",
)

DIAS = {
    "Todo dia": {0, 1, 2, 3, 4, 5, 6},
    "Seg a Sex": {0, 1, 2, 3, 4},
    "Segunda": {0},
    "Terça": {1},
    "Quarta": {2},
    "Quinta": {3},
    "Sexta": {4},
    "Sábado": {5},
    "Domingo": {6},
    "Seg/Qua/Sex": {0, 2, 4},
    "Ter/Qui": {1, 3},
    "Fins de semana": {5, 6},
}


def conectar():
    con = sqlite3.connect(str(DB_F))
    con.row_factory = sqlite3.Row
    return con


def migrar():
    with conectar() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS checklist_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                frequencia TEXT NOT NULL DEFAULT 'Todo dia',
                ordem INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS checklist_execucoes (
                item_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                concluido INTEGER DEFAULT 0,
                PRIMARY KEY (item_id, data)
            )
            """
        )

        con.commit()


migrar()


def criar_item(texto, frequencia):
    texto = texto.strip()

    if not texto:
        return

    with conectar() as con:
        ordem = con.execute(
            """
            SELECT COALESCE(MAX(ordem), 0) + 1
            FROM checklist_itens
            WHERE ativo=1
            """
        ).fetchone()[0]

        con.execute(
            """
            INSERT INTO checklist_itens
            (texto, frequencia, ordem)
            VALUES (?, ?, ?)
            """,
            (
                texto,
                frequencia,
                ordem,
            ),
        )

        con.commit()


def excluir_item(item_id):
    with conectar() as con:
        con.execute(
            """
            UPDATE checklist_itens
            SET ativo=0
            WHERE id=?
            """,
            (item_id,),
        )

        con.commit()


def marcar_item(item_id, concluido):
    hoje = datetime.date.today().isoformat()

    with conectar() as con:
        con.execute(
            """
            INSERT INTO checklist_execucoes
            (item_id, data, concluido)
            VALUES (?, ?, ?)

            ON CONFLICT(item_id, data)
            DO UPDATE SET
                concluido=excluded.concluido
            """,
            (
                item_id,
                hoje,
                int(bool(concluido)),
            ),
        )

        con.commit()


def listar_hoje():
    hoje = datetime.date.today()
    dia = hoje.weekday()

    with conectar() as con:
        rows = con.execute(
            """
            SELECT
                i.id,
                i.texto,
                i.frequencia,
                COALESCE(e.concluido, 0) AS concluido

            FROM checklist_itens i

            LEFT JOIN checklist_execucoes e
                ON e.item_id=i.id
                AND e.data=?

            WHERE i.ativo=1

            ORDER BY
                i.ordem,
                i.id
            """,
            (hoje.isoformat(),),
        ).fetchall()

    resultado = []

    for row in rows:
        frequencia = row["frequencia"]

        if dia not in DIAS.get(
            frequencia,
            set(),
        ):
            continue

        resultado.append(
            {
                "id": row["id"],
                "texto": row["texto"],
                "frequencia": frequencia,
                "concluido": bool(
                    row["concluido"]
                ),
            }
        )

    return resultado


# ============================================================
# INTERFACE
# ============================================================

DIAS_SEMANA = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


def _cores():
    tema = load_cfg().get("tema", "escuro")

    ctk.set_appearance_mode(
        "Light" if tema == "claro" else "Dark"
    )

    return get_modern_palette(tema, "checklist")


def _fonte(size, weight="normal"):
    return ctk.CTkFont(
        family="Segoe UI",
        size=size,
        weight=weight,
    )


class _JanelaBase:
    """Janela sem borda do Windows, no mesmo estilo das demais."""

    def __init__(self, parent, titulo, largura, altura):
        self.c = _cores()

        self.win = ctk.CTkToplevel(parent)
        self.win.geometry(f"{largura}x{altura}")
        self.win.overrideredirect(True)
        self.win.configure(fg_color=self.c["bg"])
        self.win.bind("<Escape>", lambda e: self.fechar())

        self._drag = (0, 0)

        self.shell = ctk.CTkFrame(
            self.win,
            fg_color=self.c["bg"],
            corner_radius=14,
            border_width=1,
            border_color=self.c["border"],
        )
        self.shell.pack(fill="both", expand=True, padx=1, pady=1)

        barra = ctk.CTkFrame(
            self.shell,
            height=44,
            fg_color="transparent",
        )
        barra.pack(fill="x")
        barra.pack_propagate(False)

        drag = (self._drag_start, self._drag_move)

        title_icon(barra, self.c, drag=drag)
        title_text(barra, self.c, titulo, drag=drag)
        close_button(barra, self.c, self.fechar)

        barra.bind("<ButtonPress-1>", self._drag_start)
        barra.bind("<B1-Motion>", self._drag_move)

        ctk.CTkFrame(
            self.shell,
            height=1,
            fg_color=self.c["border"],
        ).pack(fill="x")

        self.body = ctk.CTkFrame(
            self.shell,
            fg_color="transparent",
        )
        self.body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(16, 16),
        )

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

    def fechar(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def _botao_primario(self, parent, texto, comando, **kw):
        return ctk.CTkButton(
            parent,
            text=texto,
            height=kw.pop("height", 32),
            corner_radius=8,
            fg_color=self.c["accent"],
            hover_color=self.c["accent_hover"],
            text_color=self.c["on_accent"],
            font=_fonte(10, "bold"),
            command=comando,
            **kw,
        )

    def _botao_secundario(self, parent, texto, comando, **kw):
        return ctk.CTkButton(
            parent,
            text=texto,
            height=kw.pop("height", 32),
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.c["hover"],
            border_width=1,
            border_color=self.c["border"],
            text_color=self.c["text"],
            font=_fonte(10),
            command=comando,
            **kw,
        )


class NovoItemWindow(_JanelaBase):

    def __init__(
        self,
        parent,
        callback,
    ):
        super().__init__(parent, "Checklist", 360, 330)

        self.callback = callback

        ctk.CTkLabel(
            self.body,
            text="Novo item",
            text_color=self.c["text"],
            font=_fonte(17, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        self._rotulo("O QUE FAZER")

        self.entry = ctk.CTkEntry(
            self.body,
            height=36,
            corner_radius=8,
            fg_color=self.c["card"],
            border_width=1,
            border_color=self.c["border"],
            text_color=self.c["text"],
            placeholder_text="Ex.: Conferir e-mails",
            placeholder_text_color=self.c["dim"],
            font=_fonte(11),
        )
        self.entry.pack(fill="x", pady=(4, 14))

        self._rotulo("QUANDO APARECE")

        self.freq = tk.StringVar(value="Seg a Sex")

        ctk.CTkComboBox(
            self.body,
            variable=self.freq,
            values=list(FREQUENCIAS),
            state="readonly",
            height=36,
            corner_radius=8,
            fg_color=self.c["card"],
            border_width=1,
            border_color=self.c["border"],
            button_color=self.c["card"],
            button_hover_color=self.c["hover"],
            dropdown_fg_color=self.c["card"],
            dropdown_hover_color=self.c["hover"],
            dropdown_text_color=self.c["text"],
            text_color=self.c["text"],
            font=_fonte(11),
            dropdown_font=_fonte(11),
        ).pack(fill="x", pady=(4, 0))

        rodape = ctk.CTkFrame(self.body, fg_color="transparent")
        rodape.pack(side="bottom", fill="x")
        rodape.grid_columnconfigure((0, 1), weight=1, uniform="b")

        self._botao_secundario(
            rodape, "Cancelar", self.fechar, height=36,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self._botao_primario(
            rodape, "Adicionar", self.salvar, height=36,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.entry.bind("<Return>", lambda event: self.salvar())

        position_near(self.win, parent)

        self.win.after(120, self._focar)

    def _rotulo(self, texto):
        ctk.CTkLabel(
            self.body,
            text=texto,
            text_color=self.c["dim"],
            font=_fonte(9, "bold"),
        ).pack(anchor="w")

    def _focar(self):
        try:
            self.win.focus_force()
            self.entry.focus_set()
        except Exception:
            pass

    def salvar(self):
        texto = self.entry.get().strip()

        if not texto:
            self.entry.configure(border_color=self.c["red"])
            return

        criar_item(
            texto,
            self.freq.get(),
        )

        self.fechar()
        self.callback()


class ChecklistWindow(_JanelaBase):

    def __init__(self, parent):
        super().__init__(parent, "Checklist", 470, 600)

        topo = ctk.CTkFrame(self.body, fg_color="transparent")
        topo.pack(fill="x")

        ctk.CTkLabel(
            topo,
            text="Checklist diário",
            text_color=self.c["text"],
            font=_fonte(17, "bold"),
        ).pack(side="left")

        self._botao_primario(
            topo, "+ Adicionar", self.novo, width=100, height=30,
        ).pack(side="right")

        hoje = datetime.date.today()

        ctk.CTkLabel(
            self.body,
            text=(
                f"{DIAS_SEMANA[hoje.weekday()].capitalize()}, "
                f"{hoje.strftime('%d/%m/%Y')}"
            ),
            text_color=self.c["dim"],
            font=_fonte(10),
        ).pack(anchor="w", pady=(2, 14))

        # Progresso do dia
        progresso = ctk.CTkFrame(
            self.body,
            fg_color=self.c["card"],
            corner_radius=10,
            border_width=1,
            border_color=self.c["border"],
        )
        progresso.pack(fill="x", pady=(0, 14))

        linha = ctk.CTkFrame(progresso, fg_color="transparent")
        linha.pack(fill="x", padx=14, pady=(12, 6))

        self.lbl_progresso = ctk.CTkLabel(
            linha,
            text="",
            text_color=self.c["text"],
            font=_fonte(11, "bold"),
        )
        self.lbl_progresso.pack(side="left")

        self.lbl_percentual = ctk.CTkLabel(
            linha,
            text="",
            text_color=self.c["dim"],
            font=_fonte(10),
        )
        self.lbl_percentual.pack(side="right")

        self.barra = ctk.CTkProgressBar(
            progresso,
            height=6,
            corner_radius=3,
            fg_color=self.c["surface"],
            progress_color=self.c["accent"],
        )
        self.barra.pack(fill="x", padx=14, pady=(0, 14))
        self.barra.set(0)

        self.lista = ctk.CTkScrollableFrame(
            self.body,
            fg_color="transparent",
            scrollbar_button_color=self.c["border"],
            scrollbar_button_hover_color=self.c["dim"],
        )
        self.lista.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.body,
            text="Os itens voltam a ficar pendentes todos os dias.",
            text_color=self.c["dim"],
            font=_fonte(9),
        ).pack(anchor="w", pady=(8, 0))

        self.refresh()

        position_near(
            self.win,
            parent,
        )

    def novo(self):
        NovoItemWindow(
            self.win,
            self.refresh,
        )

    def toggle(
        self,
        item,
    ):
        marcar_item(
            item["id"],
            not item["concluido"],
        )

        self.refresh()

    def excluir(
        self,
        item,
    ):
        ok = messagebox.askyesno(
            "Excluir",
            f"Excluir '{item['texto']}' do checklist?",
            parent=self.win,
        )

        if not ok:
            return

        excluir_item(
            item["id"]
        )

        self.refresh()

    def linha(
        self,
        item,
    ):
        feito = item["concluido"]

        card = ctk.CTkFrame(
            self.lista,
            fg_color=self.c["card"],
            corner_radius=10,
            border_width=1,
            border_color=self.c["border"],
        )
        card.pack(fill="x", padx=(0, 6), pady=(0, 8))

        check = ctk.CTkCheckBox(
            card,
            text="",
            width=20,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=10,
            border_width=1,
            fg_color=self.c["done_bg"],
            hover_color=self.c["done_bg"],
            border_color=(
                self.c["done_fg"] if feito else self.c["border"]
            ),
            checkmark_color=self.c["done_fg"],
            command=lambda i=item: self.toggle(i),
        )
        if feito:
            check.select()
        check.pack(side="left", padx=(12, 8), pady=12)

        ctk.CTkLabel(
            card,
            text=item["texto"],
            anchor="w",
            text_color=self.c["dim"] if feito else self.c["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="normal" if feito else "bold",
                overstrike=feito,
            ),
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            card,
            text="Excluir",
            width=50,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color=self.c["hover"],
            text_color=self.c["red"],
            font=_fonte(9),
            command=lambda i=item: self.excluir(i),
        ).pack(side="right", padx=(0, 8))

        ctk.CTkLabel(
            card,
            text=f"  {item['frequencia']}  ",
            height=19,
            corner_radius=6,
            fg_color=self.c["surface"],
            text_color=self.c["dim"],
            font=_fonte(8, "bold"),
        ).pack(side="right", padx=(6, 4))

    def atualizar_progresso(self, itens):
        total = len(itens)

        feitos = sum(
            1
            for item in itens
            if item["concluido"]
        )

        self.lbl_progresso.configure(
            text=(
                f"{feitos} de {total} concluído"
                if total == 1
                else f"{feitos} de {total} concluídos"
            )
        )

        fracao = feitos / total if total else 0

        self.lbl_percentual.configure(
            text=f"{round(fracao * 100)}%"
        )

        self.barra.configure(
            progress_color=(
                self.c["green"]
                if total and feitos == total
                else self.c["accent"]
            )
        )
        self.barra.set(fracao)

    def refresh(self):
        for widget in (
            self.lista.winfo_children()
        ):
            widget.destroy()

        itens = listar_hoje()

        if not itens:
            vazio = ctk.CTkFrame(self.lista, fg_color="transparent")
            vazio.pack(fill="x", pady=50)

            ctk.CTkLabel(
                vazio,
                text="Nenhum item para hoje",
                text_color=self.c["text"],
                font=_fonte(12, "bold"),
            ).pack()

            ctk.CTkLabel(
                vazio,
                text=(
                    "Adicione hábitos e rotinas que se repetem,\n"
                    "como conferir e-mails ou beber água."
                ),
                text_color=self.c["dim"],
                justify="center",
                font=_fonte(10),
            ).pack(pady=(4, 14))

            self._botao_secundario(
                vazio, "+ Adicionar item", self.novo, width=140,
            ).pack()

        else:
            for item in itens:
                self.linha(item)

        self.atualizar_progresso(itens)


def abrir_checklist(parent):
    return ChecklistWindow(parent)


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    abrir_checklist(root)

    root.mainloop()
