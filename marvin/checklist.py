import datetime
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from .database import DB_F
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


class NovoItemWindow:

    def __init__(
        self,
        parent,
        callback,
    ):
        self.callback = callback

        self.win = tk.Toplevel(parent)
        self.win.title("Novo item")
        self.win.geometry("360x220")
        self.win.resizable(False, False)

        tk.Label(
            self.win,
            text="Novo item do checklist",
            font=("Segoe UI", 14, "bold"),
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15),
        )

        tk.Label(
            self.win,
            text="Tarefa",
        ).pack(
            anchor="w",
            padx=20,
        )

        self.texto = tk.StringVar()

        self.entry = ttk.Entry(
            self.win,
            textvariable=self.texto,
        )

        self.entry.pack(
            fill="x",
            padx=20,
            pady=(4, 12),
        )

        tk.Label(
            self.win,
            text="Quando aparece",
        ).pack(
            anchor="w",
            padx=20,
        )

        self.freq = tk.StringVar(
            value="Seg a Sex"
        )

        ttk.Combobox(
            self.win,
            textvariable=self.freq,
            values=FREQUENCIAS,
            state="readonly",
        ).pack(
            fill="x",
            padx=20,
            pady=(4, 15),
        )

        ttk.Button(
            self.win,
            text="Adicionar",
            command=self.salvar,
        ).pack(
            anchor="e",
            padx=20,
        )

        self.entry.bind(
            "<Return>",
            lambda event: self.salvar(),
        )

        self.entry.focus_set()


    def salvar(self):
        texto = self.texto.get().strip()

        if not texto:
            return

        criar_item(
            texto,
            self.freq.get(),
        )

        self.win.destroy()
        self.callback()


class ChecklistWindow:

    def __init__(self, parent):
        self.win = tk.Toplevel(parent)

        self.win.title(
            "MARVIN — Checklist diário"
        )

        self.win.geometry(
            "470x600"
        )

        self.vars = {}

        topo = tk.Frame(self.win)

        topo.pack(
            fill="x",
            padx=20,
            pady=(20, 10),
        )

        tk.Label(
            topo,
            text="Checklist diário",
            font=("Segoe UI", 17, "bold"),
        ).pack(
            side="left"
        )

        ttk.Button(
            topo,
            text="+ Adicionar",
            command=self.novo,
        ).pack(
            side="right"
        )

        hoje = datetime.date.today()

        self.lbl_data = tk.Label(
            self.win,
            text=hoje.strftime("%d/%m/%Y"),
            fg="#777777",
        )

        self.lbl_data.pack(
            anchor="w",
            padx=20,
        )

        self.lbl_progresso = tk.Label(
            self.win,
            text="",
            font=("Segoe UI", 10, "bold"),
        )

        self.lbl_progresso.pack(
            anchor="w",
            padx=20,
            pady=(10, 8),
        )

        ttk.Separator(
            self.win
        ).pack(
            fill="x",
            padx=20,
        )

        self.lista = tk.Frame(
            self.win
        )

        self.lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

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
        item_id,
    ):
        var = self.vars[item_id]

        marcar_item(
            item_id,
            var.get(),
        )

        self.atualizar_progresso()


    def excluir(
        self,
        item,
    ):
        ok = messagebox.askyesno(
            "Excluir",
            f"Excluir '{item['texto']}'?",
            parent=self.win,
        )

        if not ok:
            return

        excluir_item(
            item["id"]
        )

        self.refresh()


    def menu_item(
        self,
        event,
        item,
    ):
        menu = tk.Menu(
            self.win,
            tearoff=0,
        )

        menu.add_command(
            label="Excluir",
            command=lambda:
                self.excluir(item),
        )

        menu.tk_popup(
            event.x_root,
            event.y_root,
        )


    def linha(
        self,
        item,
    ):
        frame = tk.Frame(
            self.lista
        )

        frame.pack(
            fill="x",
            pady=4,
        )

        var = tk.BooleanVar(
            value=item["concluido"]
        )

        self.vars[
            item["id"]
        ] = var

        check = ttk.Checkbutton(
            frame,
            variable=var,
            command=lambda i=item["id"]:
                self.toggle(i),
        )

        check.pack(
            side="left"
        )

        texto = tk.Label(
            frame,
            text=item["texto"],
            anchor="w",
            font=("Segoe UI", 10),
        )

        texto.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
        )

        freq = tk.Label(
            frame,
            text=item["frequencia"],
            fg="#888888",
            font=("Segoe UI", 8),
        )

        freq.pack(
            side="right"
        )

        for widget in (
            frame,
            texto,
            freq,
        ):
            widget.bind(
                "<Button-3>",
                lambda e, i=item:
                    self.menu_item(e, i),
            )


    def atualizar_progresso(self):
        itens = listar_hoje()

        total = len(itens)

        feitos = sum(
            1
            for item in itens
            if item["concluido"]
        )

        self.lbl_progresso.config(
            text=f"{feitos} de {total} concluídos"
        )


    def refresh(self):
        for widget in (
            self.lista.winfo_children()
        ):
            widget.destroy()

        self.vars.clear()

        itens = listar_hoje()

        if not itens:
            tk.Label(
                self.lista,
                text=(
                    "Nenhum item para hoje.\n\n"
                    "Clique em + Adicionar."
                ),
                fg="#777777",
                font=("Segoe UI", 10),
            ).pack(
                pady=70
            )

        else:
            for item in itens:
                self.linha(item)

        self.atualizar_progresso()


def abrir_checklist(parent):
    return ChecklistWindow(parent)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    abrir_checklist(root)

    root.mainloop()