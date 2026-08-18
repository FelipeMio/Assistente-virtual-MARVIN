import tkinter as tk
import threading, math, time, datetime, json, random, sys, textwrap
from pathlib import Path
from tkinter import messagebox

from .database import (
    db_criar,
    db_listar,
    db_concluir,
    db_excluir,
    db_alterar,
    db_marcar_lembrado,
    db_reset_lembrado,
    db_adiar,
    db_streak_hoje,
    db_limpar_antigas,
    db_obter,
)


# ARMAZENAMENTO

HOME = Path.home() / ".marvin"
HOME.mkdir(exist_ok=True)

CFG_F = HOME / "config.json"

_CFG_DEFAULTS = {
    "pos_x": None,
    "pos_y": None,
    "nao_perturbe": False,
    "som": True,
    "opacidade": 1.0,
}


def _load_cfg():
    if CFG_F.exists():
        try:
            d = json.loads(CFG_F.read_text("utf-8"))
            return {**_CFG_DEFAULTS, **d}
        except Exception:
            pass

    return dict(_CFG_DEFAULTS)


cfg = _load_cfg()


def save_cfg():
    CFG_F.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2),
        "utf-8"
    )

#  SOM NATIVO


def _beep():
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


#  PALETA

TK = "#010203"  # cor de transparencia Windows

C = dict(
    win_bg  = "#0d1117",
    panel   = "#161b22",
    border  = "#30363d",
    text    = "#e6edf3",
    dim     = "#7d8590",
    accent  = "#58a6ff",
    green   = "#3fb950",
    red     = "#f85149",
    orange  = "#d29922",
    purple  = "#bc8cff",
    bub_bg  = "#161b22",
    bub_bd  = "#58a6ff",
)

#  PIXEL ART DO MARVIN

_PAL = {
    " ": None,
    "#": "#000000",
    "D": "#2e2f34",
    "B": "#2c334d",
    "W": "#f9f6e9",
    "R": "#9f2929",
    "P": "#d77c78",
    "G": "#a0aab1",
}

GATO = [
    "     ##           ##    ",
    "    #DD#         #DDD   ",
    "    #PDD#       #DPPD   ",
    "    #PPDD#######DPPPD   ",
    "    #PPPDDDDDDDDPPPPD   ",
    "    #PPDDDDDDDDDDPPPD   ",
    "    #PDDDDDDDDDDDDDPD   ",
    "    #DDDDDDWGDDDDDDD#   ",
    "    #DDDDD#WGDDDDDDDD   ",
    "   #DDD#DDWWWD#DDDDDDG  ",
    "WWWBGDDG#DWWWDG#DDDGGGWW",
    "WWW#DDDDDWWWWBDDDDDDDBWW",
    "   #GDDDWWGPWWWDDDDGGB  ",
    " GGGDDDWWWGWWWWWWDDDGGG ",
    "    #WWWWWG##WWWWWW #   ",
    "     #WWWWWWWWWWWWW#    ",
    "      #WWWWWWWWWW##     ",
    "      ###########B##    ",
    "     #BB#WRRG #BBBBB#   ",
    "    #BBBBBGRG #BBBBB#   ",
    "    #BBBBBGRGBBBBBBBB#  ",
    "   #BBBBBBGRGBBBBBBBB#  ",
    "   #B#BBBDRRRBBBBB#BBB# ",
    "  #BB#BBBBDRRBBBBB#BBB# ",
    "  #BB#BBBBDDBBBBBB#BBB# ",
    "  #BB#BBBBBBBBBBBB#BBB# ",
    "  #BB#BBBBBBBBBBBB#BBB# ",
    "  ####BBBBBBBBBBBB##### ",
    "  #WW#BBBBBBBBBBBB#GWW# ",
    "  W###BBBBBBBBBBBBB###W ",
    "     ###############    ",
    "      #BBBBBBBBBBBB#    ",
    "      #BBBBBBBBBBBB#    ",
    "      #BBBD##DBBBB#     ",
    "       #BBDW DBBBB#     ",
    "       #BBDW  #BBB#     ",
    "       ####W  #####     ",
    "     G#WWWGGGG#WWWW#G   ",
    "    GGBBBBBGGGG#BBBBGG  ",
    "      GGGGGGGGGGGGGG    ",
]

CAT_COLS = 24
CAT_ROWS = 40
PX       = 4


def _cor_pixel(ch, row, col, t, state, blink):
    if blink and 7 <= row <= 10 and ch in ("#", "W"):
        if (7 <= col <= 8) or (13 <= col <= 14):
            return _PAL["D"]
    if ch == "R" and state == "alert":
        p  = abs(math.sin(t * 6))
        rv = int(0x9f + p * (0xff - 0x9f))
        gv = int(0x29 * (1 - p) + 0xaa * p)
        bv = int(0x29 * (1 - p))
        return f"#{rv:02x}{gv:02x}{bv:02x}"
    return _PAL.get(ch)


def draw_cat(cv, t, state, W, H):
    cv.delete("all")
    bob     = math.sin(t * 1.4) * 3
    total_w = CAT_COLS * PX
    total_h = CAT_ROWS * PX
    ox      = (W - total_w) // 2
    oy      = int(H - total_h - 8 + bob)

    
    # Halo alert
    if state == "alert":
        p    = abs(math.sin(t * 4))
        rv   = int(160 + p * 80)
        gv   = int(60  + p * 60)
        hcol = f"#{rv:02x}{gv:02x}00"
        for dr in (3, 7, 12):
            cv.create_rectangle(ox - dr, oy - dr,
                                 ox + total_w + dr, oy + total_h + dr,
                                 fill="", outline=hcol, width=1)

    # Halo thinking
    if state == "thinking":
        p    = abs(math.sin(t * 2))
        bv   = int(80 + p * 80)
        hcol = f"#00{bv:02x}ff"
        for dr in (3, 7):
            cv.create_rectangle(ox - dr, oy - dr,
                                 ox + total_w + dr, oy + total_h + dr,
                                 fill="", outline=hcol, width=1)

    arm_shift = int(math.sin(t * 7) * 9) if state == "alert" else 0
    blink     = (int(t * 2.0) % 100 < 4)

    for row_i, linha in enumerate(GATO):
        for col_i, ch in enumerate(linha):
            if ch == " ":
                continue
            cor = _cor_pixel(ch, row_i, col_i, t, state, blink)
            if cor is None:
                continue
            dy = arm_shift if (state == "alert"
                               and 20 <= row_i <= 28
                               and 20 <= col_i <= 23) else 0
            x0 = ox + col_i * PX
            y0 = oy + row_i * PX + dy
            cv.create_rectangle(x0, y0, x0 + PX, y0 + PX,
                                 fill=cor, outline="")


def draw_bubble(cv, t, cx, top_y, text, W):
    wrapped = textwrap.wrap(text, width=26)[:4]
    if not wrapped:
        return
    line_h, py = 15, 9
    bw  = min(220, W + 60)
    bh  = len(wrapped) * line_h + py * 2
    bx  = max(6, cx - bw // 2)
    by  = max(6, top_y - bh - 16)
    cv.create_rectangle(bx+2, by+2, bx+bw+2, by+bh+2,
                         fill="#060c14", outline="")
    cv.create_rectangle(bx, by, bx+bw, by+bh,
                         fill=C["bub_bg"], outline=C["bub_bd"], width=2)
    tip = min(max(cx, bx+16), bx+bw-16)
    cv.create_polygon([tip-7, by+bh, tip+7, by+bh, tip, top_y-2],
                       fill=C["bub_bg"], outline=C["bub_bd"])
    cv.create_line(bx+2, by+bh, tip-7, by+bh,
                   fill=C["bub_bd"], width=2)
    cv.create_line(tip+7, by+bh, bx+bw-2, by+bh,
                   fill=C["bub_bd"], width=2)
    for i, line in enumerate(wrapped):
        cv.create_text(bx+bw//2, by+py+i*line_h+line_h//2,
                        text=line, fill=C["text"],
                        font=("Consolas", 8), anchor="center")

#  FRASES IDLE

_IDLE_MSGS = [
    
    "Clique com botao esquerdo para o menu.",
    "Clique com botao direito para o menu.",
  
    
]

def _frase_saudacao(n):
    hora = datetime.datetime.now().hour
    saud = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
    if n:
        return f"{saud}! {n} tarefa(s) pendente(s)."
    return f"{saud}! Sem tarefas pendentes."

#  HELPERS DE UI

REPEAT_OPTS = ["Nunca", "Todo dia", "Toda semana",
               "Seg/Qua/Sex", "Seg a Sex", "Fins de semana"]


def _make_win(parent, title, w, h, resizable=False):
    win = tk.Toplevel(parent)
    win.title(f"Marvin - {title}")
    win.configure(bg=C["win_bg"])
    win.geometry(f"{w}x{h}")
    win.attributes("-topmost", True)
    win.resizable(resizable, resizable)
    return win


def _header(win, title):
    hf = tk.Frame(win, bg=C["panel"], height=42)
    hf.pack(fill="x")
    hf.pack_propagate(False)
    tk.Label(hf, text=f"  {title}", bg=C["panel"], fg=C["accent"],
              font=("Consolas", 10, "bold")).pack(side="left", padx=10, pady=10)
    tk.Button(hf, text=" x ", bg=C["panel"], fg=C["dim"], bd=0,
               font=("Consolas", 10), cursor="hand2",
               activebackground=C["panel"], activeforeground=C["red"],
               command=win.destroy).pack(side="right", padx=8)
    tk.Frame(win, bg=C["border"], height=1).pack(fill="x")


def _lbl(parent, text):
    tk.Label(parent, text=text, bg=C["win_bg"], fg=C["dim"],
              font=("Consolas", 8, "bold")).pack(anchor="w", pady=(8, 2))


def _entry(parent, var, width=None):
    kw = {"width": width} if width else {}
    e = tk.Entry(parent, textvariable=var,
                  bg=C["panel"], fg=C["text"],
                  insertbackground=C["accent"],
                  font=("Consolas", 9), bd=0, relief="flat", **kw)
    e.pack(fill="x" if not width else None, ipady=6)
    return e


def _option_menu(parent, var):
    opt = tk.OptionMenu(parent, var, *REPEAT_OPTS)
    opt.config(bg=C["panel"], fg=C["text"],
                activebackground=C["border"],
                activeforeground=C["text"],
                font=("Consolas", 9),
                highlightthickness=0, bd=0)
    opt["menu"].config(bg=C["panel"], fg=C["text"],
                        activebackground=C["border"],
                        activeforeground=C["text"],
                        font=("Consolas", 9))
    opt.pack(fill="x", ipady=4)
    return opt


def _validate_date(s):
    try:
        return datetime.datetime.strptime(s.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def _validate_time(s):
    try:
        datetime.datetime.strptime(s.strip(), "%H:%M")
        return s.strip()
    except ValueError:
        return None

#  JANELA: NOVA TAREFA

class NewTaskWindow:
    def __init__(self, parent, companion, prefill=""):
        self.comp = companion
        self.win  = _make_win(parent, "Nova Tarefa", 400, 385)
        self.win.grab_set()
        self._build(prefill)

    def _build(self, prefill):
        w = self.win
        _header(w, "Nova Tarefa")
        body = tk.Frame(w, bg=C["win_bg"])
        body.pack(fill="both", expand=True, padx=20, pady=8)

        _lbl(body, "Titulo da tarefa *")
        self.v_txt = tk.StringVar(value=prefill)
        self.e_txt = _entry(body, self.v_txt)

        _lbl(body, "Descricao (opcional)")
        self.v_desc = tk.StringVar()
        _entry(body, self.v_desc)

        row = tk.Frame(body, bg=C["win_bg"])
        row.pack(fill="x", pady=(4, 0))
        Lf = tk.Frame(row, bg=C["win_bg"])
        Lf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        Rf = tk.Frame(row, bg=C["win_bg"])
        Rf.pack(side="left")

        tk.Label(Lf, text="Data (DD/MM/AAAA) *",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 8, "bold")).pack(anchor="w", pady=(8, 2))
        self.v_data = tk.StringVar(
            value=datetime.date.today().strftime("%d/%m/%Y"))
        self.e_data = tk.Entry(Lf, textvariable=self.v_data,
                                bg=C["panel"], fg=C["text"],
                                insertbackground=C["accent"],
                                font=("Consolas", 9), bd=0, relief="flat",
                                width=13)
        self.e_data.pack(fill="x", ipady=6)

        tk.Label(Rf, text="Horario (HH:MM) *",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 8, "bold")).pack(anchor="w", pady=(8, 2))
        self.v_hora = tk.StringVar(
            value=datetime.datetime.now().strftime("%H:%M"))
        self.e_hora = tk.Entry(Rf, textvariable=self.v_hora,
                                bg=C["panel"], fg=C["text"],
                                insertbackground=C["accent"],
                                font=("Consolas", 9), bd=0, relief="flat",
                                width=7)
        self.e_hora.pack(ipady=6)

        self.v_data.trace_add("write", self._validate_live)
        self.v_hora.trace_add("write", self._validate_live)

        _lbl(body, "Repeticao")
        self.v_rep = tk.StringVar(value=REPEAT_OPTS[0])
        _option_menu(body, self.v_rep)

        self.v_err = tk.StringVar()
        tk.Label(body, textvariable=self.v_err, bg=C["win_bg"], fg=C["red"],
                  font=("Consolas", 8)).pack(anchor="w", pady=(4, 0))

        bf = tk.Frame(body, bg=C["win_bg"])
        bf.pack(anchor="w", pady=8)
        tk.Button(bf, text="  Salvar  ",
                   bg=C["green"], fg=C["win_bg"], bd=0,
                   padx=14, pady=7, font=("Consolas", 9, "bold"),
                   cursor="hand2",
                   activebackground=C["accent"],
                   activeforeground=C["win_bg"],
                   command=self._salvar).pack(side="left")
        tk.Button(bf, text="  Cancelar  ",
                   bg=C["panel"], fg=C["dim"], bd=0,
                   padx=10, pady=7, font=("Consolas", 9),
                   cursor="hand2",
                   activebackground=C["border"],
                   activeforeground=C["text"],
                   command=self.win.destroy).pack(side="left", padx=8)

        self.e_txt.focus()
        self.win.bind("<Return>", lambda e: self._salvar())
        self.win.bind("<Escape>", lambda e: self.win.destroy())

    def _validate_live(self, *_):
        d_ok = _validate_date(self.v_data.get()) is not None
        h_ok = _validate_time(self.v_hora.get())  is not None
        self.e_data.config(fg=C["text"] if d_ok else C["red"])
        self.e_hora.config(fg=C["text"] if h_ok else C["red"])

    def _salvar(self):
        texto = self.v_txt.get().strip()
        desc  = self.v_desc.get().strip()
        data  = _validate_date(self.v_data.get())
        hora  = _validate_time(self.v_hora.get())
        if not texto:
            self.v_err.set("Digite o titulo da tarefa."); return
        if data is None:
            self.v_err.set("Data invalida. Use DD/MM/AAAA."); return
        if hora is None:
            self.v_err.set("Horario invalido. Use HH:MM."); return
        db_criar(texto, desc, data, hora, self.v_rep.get())
        self.comp.say("Tarefa registrada!", "talking", 3000)
        self.win.destroy()

#  JANELA: LISTA DE TAREFAS

class TaskWindow:
    def __init__(self, parent, companion):
        self.comp   = companion
        self.parent = parent
        self.win    = _make_win(parent, "Tarefas", 440, 520, resizable=True)
        self._build()

    def _build(self):
        w = self.win
        hf = tk.Frame(w, bg=C["panel"], height=42)
        hf.pack(fill="x")
        hf.pack_propagate(False)
        tk.Label(hf, text="  Tarefas", bg=C["panel"], fg=C["accent"],
                  font=("Consolas", 10, "bold")).pack(
                      side="left", padx=10, pady=10)
        tk.Button(hf, text=" x ", bg=C["panel"], fg=C["dim"], bd=0,
                   font=("Consolas", 10), cursor="hand2",
                   activebackground=C["panel"], activeforeground=C["red"],
                   command=w.destroy).pack(side="right", padx=8)
        tk.Button(hf, text=" + ", bg=C["panel"], fg=C["green"], bd=0,
                   font=("Consolas", 13, "bold"), cursor="hand2",
                   activebackground=C["panel"], activeforeground=C["text"],
                   command=lambda: NewTaskWindow(self.parent, self.comp)
                   ).pack(side="right", padx=4)
        tk.Frame(w, bg=C["border"], height=1).pack(fill="x")

        self.sv = tk.StringVar()
        tk.Label(w, textvariable=self.sv, bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 7)).pack(anchor="w", padx=14, pady=3)

        # Filtros
        fbar = tk.Frame(w, bg=C["win_bg"])
        fbar.pack(fill="x", padx=10, pady=(0, 4))
        self.filtro = tk.StringVar(value="todas")
        for label, val in [("Todas", "todas"),
                            ("Pendentes", "pendentes"),
                            ("Concluidas", "concluidas")]:
            tk.Radiobutton(fbar, text=label,
                            variable=self.filtro, value=val,
                            bg=C["win_bg"], fg=C["dim"],
                            selectcolor=C["panel"],
                            activebackground=C["win_bg"],
                            activeforeground=C["text"],
                            font=("Consolas", 8),
                            command=self._refresh).pack(side="left", padx=6)

        # Lista
        outer = tk.Frame(w, bg=C["win_bg"])
        outer.pack(fill="both", expand=True)
        self._cv = tk.Canvas(outer, bg=C["win_bg"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self._cv.yview,
                           bg=C["panel"], troughcolor=C["win_bg"])
        self._cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._cv.pack(side="left", fill="both", expand=True)
        self.lf = tk.Frame(self._cv, bg=C["win_bg"])
        self._cv.create_window((0, 0), window=self.lf, anchor="nw")
        self.lf.bind("<Configure>",
                      lambda e: self._cv.configure(
                          scrollregion=self._cv.bbox("all")))
        self._cv.bind_all("<MouseWheel>",
                           lambda e: self._cv.yview_scroll(
                               -1 if e.delta > 0 else 1, "units"))
        self._refresh()

    def _refresh(self):
        for widget in self.lf.winfo_children():
            widget.destroy()

        rows    = db_listar()
        filtro  = self.filtro.get()
        streak  = db_streak_hoje()
        pending = [r for r in rows if not r[6]]
        done_l  = [r for r in rows if r[6]]

        streak_txt = f"  {streak} concluida(s) hoje" if streak else ""
        self.sv.set(f"   {len(done_l)}/{len(rows)} concluidas  |  "
                    f"{len(pending)} pendente(s){streak_txt}")

        if not rows:
            tk.Label(self.lf,
                      text="Nenhuma tarefa ainda.\nClique + para criar.",
                      bg=C["win_bg"], fg=C["dim"],
                      font=("Consolas", 9, "italic"),
                      justify="center", pady=30).pack()
            return

        def section(title, lst):
            if not lst:
                return
            tk.Label(self.lf, text=title, bg=C["win_bg"], fg=C["accent"],
                      font=("Consolas", 8, "bold"), pady=4
                      ).pack(anchor="w", padx=12)
            tk.Frame(self.lf, bg=C["border"], height=1
                     ).pack(fill="x", padx=8, pady=1)
            for row in lst:
                self._row(row)

        if filtro in ("todas", "pendentes"):
            section("  TAREFAS PENDENTES", pending)
        if filtro in ("todas", "concluidas"):
            section("  TAREFAS CONCLUIDAS", done_l)

    def _row(self, row):
        tid, texto, desc, data, hora, rep, concluida, lembrado = row
        bg    = C["panel"] if not concluida else C["win_bg"]
        row_f = tk.Frame(self.lf, bg=bg)
        row_f.pack(fill="x", pady=2, padx=6)

        icon = "v" if concluida else "o"
        ic   = tk.Label(row_f, text=icon, bg=bg,
                         fg=C["green"] if concluida else C["accent"],
                         font=("Consolas", 11), padx=8, cursor="hand2")
        ic.pack(side="left")
        ic.bind("<Button-1>", lambda e, i=tid: self._toggle(i))

        info = tk.Frame(row_f, bg=bg)
        info.pack(side="left", fill="x", expand=True, pady=5)
        tk.Label(info, text=texto, bg=bg,
                  fg=C["dim"] if concluida else C["text"],
                  font=("Consolas", 9), anchor="w",
                  wraplength=220, justify="left").pack(anchor="w")

        parts = []
        try:
            d    = datetime.date.fromisoformat(data)
            hoje = datetime.date.today()
            if d == hoje:
                parts.append("Hoje")
            elif d < hoje and not concluida:
                parts.append("ATRASADA")
            else:
                parts.append(d.strftime("%d/%m/%y"))
        except Exception:
            pass
        if hora:
            parts.append(hora[:5])
        if rep != "Nunca":
            parts.append(f"rep: {rep}")
        if desc:
            parts.append(f"| {desc[:28]}")
        if parts:
            tk.Label(info, text="  ".join(parts), bg=bg, fg=C["dim"],
                      font=("Consolas", 7)).pack(anchor="w")

        bf = tk.Frame(row_f, bg=bg)
        bf.pack(side="right", padx=6)
        tk.Button(bf, text="Editar", bg=bg, fg=C["accent"], bd=0,
                   font=("Consolas", 8), cursor="hand2",
                   activebackground=C["border"],
                   activeforeground=C["text"],
                   command=lambda i=tid: EditTaskWindow(
                       self.win, self.comp, i, self._refresh)
                   ).pack(side="left", padx=2)
        tk.Button(bf, text="Excluir", bg=bg, fg=C["red"], bd=0,
                   font=("Consolas", 8), cursor="hand2",
                   activebackground=C["border"],
                   activeforeground=C["text"],
                   command=lambda i=tid: self._delete(i)
                   ).pack(side="left", padx=2)

    def _toggle(self, tid):
        for r in db_listar():
            if r[0] == tid:
                if r[6]:
                    db_alterar(tid, "concluida",    0)
                    db_alterar(tid, "lembrado",     0)
                    db_alterar(tid, "concluido_em", None)
                else:
                    db_concluir(tid)
                break
        self._refresh()
        self.comp.say("Tarefa atualizada!", "talking", 2000)

    def _delete(self, tid):
        if messagebox.askyesno("Marvin", "Excluir esta tarefa?",
                                parent=self.win):
            db_excluir(tid)
            self._refresh()

#  JANELA: EDITAR TAREFA

class EditTaskWindow:
    def __init__(self, parent, companion, tid, callback):
        self.comp     = companion
        self.tid      = tid
        self.callback = callback
        row = db_obter(tid)
        if not row:
            return
        texto, desc, data, hora, rep = row
        self.win = _make_win(parent, "Editar Tarefa", 400, 370)
        self.win.grab_set()
        self._build(texto, desc, data, hora, rep)

    def _build(self, texto, desc, data, hora, rep):
        w = self.win
        _header(w, "Editar Tarefa")
        body = tk.Frame(w, bg=C["win_bg"])
        body.pack(fill="both", expand=True, padx=20, pady=8)

        _lbl(body, "Titulo")
        self.v_txt = tk.StringVar(value=texto)
        _entry(body, self.v_txt)

        _lbl(body, "Descricao")
        self.v_desc = tk.StringVar(value=desc)
        _entry(body, self.v_desc)

        row_f = tk.Frame(body, bg=C["win_bg"])
        row_f.pack(fill="x", pady=(4, 0))
        Lf = tk.Frame(row_f, bg=C["win_bg"])
        Lf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        Rf = tk.Frame(row_f, bg=C["win_bg"])
        Rf.pack(side="left")

        tk.Label(Lf, text="Data (AAAA-MM-DD)",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 8, "bold")).pack(anchor="w", pady=(8, 2))
        self.v_data = tk.StringVar(value=data)
        _entry(Lf, self.v_data)

        tk.Label(Rf, text="Hora (HH:MM)",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 8, "bold")).pack(anchor="w", pady=(8, 2))
        self.v_hora = tk.StringVar(value=hora[:5])
        _entry(Rf, self.v_hora, width=7)

        _lbl(body, "Repeticao")
        self.v_rep = tk.StringVar(value=rep)
        _option_menu(body, self.v_rep)

        self.v_err = tk.StringVar()
        tk.Label(body, textvariable=self.v_err, bg=C["win_bg"], fg=C["red"],
                  font=("Consolas", 8)).pack(anchor="w", pady=(4, 0))

        bf = tk.Frame(body, bg=C["win_bg"])
        bf.pack(anchor="w", pady=8)
        tk.Button(bf, text="  Salvar  ",
                   bg=C["accent"], fg=C["win_bg"], bd=0,
                   padx=14, pady=7,
                   font=("Consolas", 9, "bold"), cursor="hand2",
                   activebackground=C["purple"],
                   activeforeground=C["win_bg"],
                   command=self._salvar).pack(side="left")
        tk.Button(bf, text="  Cancelar  ",
                   bg=C["panel"], fg=C["dim"], bd=0,
                   padx=10, pady=7, font=("Consolas", 9),
                   cursor="hand2",
                   activebackground=C["border"],
                   activeforeground=C["text"],
                   command=w.destroy).pack(side="left", padx=8)

        w.bind("<Return>", lambda e: self._salvar())
        w.bind("<Escape>", lambda e: w.destroy())

    def _salvar(self):
        txt = self.v_txt.get().strip()
        if not txt:
            self.v_err.set("Titulo nao pode ser vazio."); return
        db_alterar(self.tid, "texto",       txt)
        db_alterar(self.tid, "descricao",   self.v_desc.get().strip())
        db_alterar(self.tid, "data",        self.v_data.get().strip())
        db_alterar(self.tid, "hora",        self.v_hora.get().strip())
        db_alterar(self.tid, "recorrencia", self.v_rep.get())
        db_alterar(self.tid, "lembrado",    0)
        self.callback()
        self.comp.say("Tarefa editada!", "talking", 2000)
        self.win.destroy()

#  JANELA: CONFIGURACOES

class SettingsWindow:
    def __init__(self, parent, companion):
        self.comp = companion
        self.win  = _make_win(parent, "Configuracoes", 400, 310)
        self.win.grab_set()
        self._build()

    def _build(self):
        w = self.win
        _header(w, "Configuracoes")
        body = tk.Frame(w, bg=C["win_bg"])
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # Nao Perturbe
        self.v_np = tk.BooleanVar(value=cfg.get("nao_perturbe", False))
        r1 = tk.Frame(body, bg=C["win_bg"])
        r1.pack(fill="x", pady=4)
        tk.Checkbutton(r1, variable=self.v_np,
                        bg=C["win_bg"], selectcolor=C["panel"],
                        activebackground=C["win_bg"],
                        cursor="hand2").pack(side="left")
        tk.Label(r1, text="Modo Nao Perturbe (silencia lembretes)",
                  bg=C["win_bg"], fg=C["text"],
                  font=("Consolas", 9)).pack(side="left")

        # Som
        self.v_som = tk.BooleanVar(value=cfg.get("som", True))
        r2 = tk.Frame(body, bg=C["win_bg"])
        r2.pack(fill="x", pady=4)
        tk.Checkbutton(r2, variable=self.v_som,
                        bg=C["win_bg"], selectcolor=C["panel"],
                        activebackground=C["win_bg"],
                        cursor="hand2").pack(side="left")
        tk.Label(r2, text="Som ao receber lembrete",
                  bg=C["win_bg"], fg=C["text"],
                  font=("Consolas", 9)).pack(side="left")

        # Opacidade
        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=10)
        tk.Label(body, text="Opacidade do Marvin:",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 8, "bold")).pack(anchor="w")
        self.v_op = tk.DoubleVar(value=cfg.get("opacidade", 1.0))
        tk.Scale(body, variable=self.v_op,
                  from_=0.3, to=1.0, resolution=0.05,
                  orient="horizontal",
                  bg=C["win_bg"], fg=C["text"],
                  troughcolor=C["panel"],
                  highlightthickness=0,
                  activebackground=C["accent"]
                  ).pack(fill="x", pady=4)

        # Limpeza
        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=8)
        tk.Button(body,
                   text="  Limpar tarefas concluidas ha mais de 30 dias",
                   bg=C["panel"], fg=C["dim"], bd=0,
                   padx=10, pady=6, font=("Consolas", 8), cursor="hand2",
                   activebackground=C["border"],
                   activeforeground=C["text"],
                   command=self._limpar).pack(anchor="w")

        tk.Label(body, text=f"DB: {DB_F}",
                  bg=C["win_bg"], fg=C["dim"],
                  font=("Consolas", 7),
                  wraplength=360).pack(anchor="w", pady=(8, 0))

        tk.Button(body, text="  Salvar e Fechar  ",
                   bg=C["green"], fg=C["win_bg"], bd=0,
                   padx=14, pady=7,
                   font=("Consolas", 9, "bold"), cursor="hand2",
                   activebackground=C["accent"],
                   activeforeground=C["win_bg"],
                   command=self._salvar).pack(anchor="w", pady=10)

    def _salvar(self):
        cfg["nao_perturbe"] = self.v_np.get()
        cfg["som"]          = self.v_som.get()
        cfg["opacidade"]    = round(self.v_op.get(), 2)
        save_cfg()
        try:
            self.comp.root.attributes("-alpha", cfg["opacidade"])
        except Exception:
            pass
        self.comp.say("Configuracoes salvas!", "talking", 2500)
        self.win.destroy()

    def _limpar(self):
        db_limpar_antigas(30)
        self.comp.say("Limpeza concluida!", "talking", 2500)
        self.win.destroy()

#  PAINEL FLUTUANTE (clique esquerdo)

class InteractionPanel:
    def __init__(self, root, companion, mode="idle"):
        self.comp = companion
        self.root = root
        self.win  = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=C["border"])

        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = companion.W
        sw = root.winfo_screenwidth()
        px = rx - 228 if rx > 238 else rx + rw + 4
        px = max(0, min(px, sw - 240))
        self.win.geometry(f"+{px}+{max(0, ry + 20)}")

        inner = tk.Frame(self.win, bg=C["panel"])
        inner.pack(padx=1, pady=1)

        if mode == "alert":
            self._build_alert(inner)
        else:
            self._build_idle(inner)

        self.win.bind("<FocusOut>", lambda e: self._close())
        self.win.focus_force()

    def _close(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def _btn(self, parent, text, cmd, fg=None):
        b = tk.Button(parent, text=text, bg=C["win_bg"],
                       fg=fg or C["text"], bd=0,
                       padx=14, pady=7, cursor="hand2",
                       font=("Consolas", 9),
                       activebackground=C["border"],
                       activeforeground=C["text"],
                       command=cmd)
        b.pack(fill="x", padx=6, pady=2)
        return b

    def _build_idle(self, p):
        rows   = db_listar()
        n      = len([r for r in rows if not r[6]])
        hoje   = datetime.date.today().isoformat()
        n_hoje = len([r for r in rows if not r[6] and r[3] == hoje])
        streak = db_streak_hoje()

        lines = []
        if n:
            lines.append(f"{n} tarefa(s) pendente(s).")
            if n_hoje:
                lines.append(f"{n_hoje} para hoje.")
        else:
            lines.append("Nenhuma tarefa pendente.")
        if streak:
            lines.append(f"{streak} concluida(s) hoje!")
        msg = "\n".join(lines)

        tk.Label(p, text=msg, bg=C["panel"], fg=C["text"],
                  font=("Consolas", 8), pady=10, padx=12,
                  justify="center", wraplength=200).pack()
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=8)
        if n:
            self._btn(p, "Ver tarefas",
                       lambda: [self._close(),
                                 TaskWindow(self.root, self.comp)])
        self._btn(p, "+ Nova tarefa",
                   lambda: [self._close(),
                             NewTaskWindow(self.root, self.comp)])
        self._btn(p, "Agora nao", self._close, fg=C["dim"])

    def _build_alert(self, p):
        queue = self.comp._reminder_queue
        task  = queue[0] if queue else None
        name  = task[1] if task else "tarefa"
        hora  = task[4][:5] if task else ""
        tk.Label(p, text=f"Lembrete: {hora}",
                  bg=C["panel"], fg=C["orange"],
                  font=("Consolas", 8), pady=(6, 2), padx=12).pack()
        tk.Label(p, text=name,
                  bg=C["panel"], fg=C["text"],
                  font=("Consolas", 9, "bold"), pady=(0, 8), padx=12,
                  wraplength=200, justify="center").pack()
        n_fila = len(queue)
        if n_fila > 1:
            tk.Label(p, text=f"+{n_fila - 1} lembrete(s) na fila",
                      bg=C["panel"], fg=C["dim"],
                      font=("Consolas", 7), pady=2).pack()
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=8)
        self._btn(p, "Concluir",
                   lambda: [self._close(), self.comp.complete_task()],
                   fg=C["green"])
        self._btn(p, "Adiar",
                   lambda: [self._close(),
                             SnoozeWindow(self.root, self.comp, task)])
        self._btn(p, "Ver tarefas",
                   lambda: [self._close(),
                             TaskWindow(self.root, self.comp)])


class SnoozeWindow:
    OPTS = [("5 minutos", 5), ("15 minutos", 15),
            ("30 minutos", 30), ("1 hora", 60)]

    def __init__(self, root, companion, task):
        self.comp = companion
        self.task = task
        self.win  = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=C["border"])

        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = companion.W
        sw = root.winfo_screenwidth()
        px = rx - 208 if rx > 218 else rx + rw + 4
        px = max(0, min(px, sw - 220))
        self.win.geometry(f"+{px}+{max(0, ry + 20)}")

        inner = tk.Frame(self.win, bg=C["panel"])
        inner.pack(padx=1, pady=1)
        tk.Label(inner, text="Adiar por quanto tempo?",
                  bg=C["panel"], fg=C["text"],
                  font=("Consolas", 8), pady=8, padx=12).pack()
        tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", padx=8)
        for lbl, mins in self.OPTS:
            tk.Button(inner, text=lbl,
                       bg=C["win_bg"], fg=C["text"], bd=0,
                       padx=14, pady=7, cursor="hand2",
                       font=("Consolas", 9),
                       activebackground=C["border"],
                       activeforeground=C["text"],
                       command=lambda m=mins: self._snooze(m)
                       ).pack(fill="x", padx=6, pady=2)
        tk.Button(inner, text="Cancelar",
                   bg=C["win_bg"], fg=C["dim"], bd=0,
                   padx=14, pady=5, cursor="hand2",
                   font=("Consolas", 8),
                   activebackground=C["border"],
                   command=self._close).pack(fill="x", padx=6, pady=2)
        self.win.bind("<FocusOut>", lambda e: self._close())
        self.win.focus_force()

    def _close(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def _snooze(self, minutes):
        new_dt = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        if self.task:
            db_adiar(self.task[0],
                     new_dt.strftime("%Y-%m-%d"),
                     new_dt.strftime("%H:%M"))
        self.comp._next_reminder()
        self.comp.say(f"Adiado para {new_dt.strftime('%H:%M')}.",
                       "talking", 3000)
        self._close()

#  POPUP DE NOTIFICACAO (canto inferior direito)

class NotifPopup:
    def __init__(self, root, title, body_text, duration=6000):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=C["border"])

        inner = tk.Frame(self.win, bg=C["panel"])
        inner.pack(padx=1, pady=1)

        hf = tk.Frame(inner, bg=C["panel"])
        hf.pack(fill="x", padx=8, pady=(8, 2))
        tk.Label(hf, text=f"Lembrete: {title}",
                  bg=C["panel"], fg=C["orange"],
                  font=("Consolas", 9, "bold"),
                  wraplength=220, justify="left").pack(side="left")
        tk.Button(hf, text="x", bg=C["panel"], fg=C["dim"], bd=0,
                   font=("Consolas", 8), cursor="hand2",
                   activebackground=C["panel"], activeforeground=C["red"],
                   command=self.win.destroy).pack(side="right")

        if body_text:
            tk.Label(inner, text=body_text,
                      bg=C["panel"], fg=C["dim"],
                      font=("Consolas", 8),
                      wraplength=220, justify="left"
                      ).pack(anchor="w", padx=8, pady=(0, 8))

        self._bar_w    = 220
        self._progress = tk.Frame(inner, bg=C["accent"],
                                   height=3, width=self._bar_w)
        self._progress.pack(fill="x")

        self.win.update_idletasks()
        sw  = self.win.winfo_screenwidth()
        sh  = self.win.winfo_screenheight()
        ww  = self.win.winfo_width()
        wh  = self.win.winfo_height()
        self.win.geometry(f"+{sw - ww - 16}+{sh - wh - 56}")

        self._duration = duration
        self._elapsed  = 0
        self._tick     = 50
        self._countdown()

    def _countdown(self):
        self._elapsed += self._tick
        remaining = max(0, self._duration - self._elapsed)
        frac      = remaining / self._duration
        new_w     = max(1, int(self._bar_w * frac))
        try:
            self._progress.config(width=new_w)
            if remaining <= 0:
                self.win.destroy()
            else:
                self.win.after(self._tick, self._countdown)
        except Exception:
            pass

#  PERSONAGEM PRINCIPAL — MARVIN

class MarvinCompanion:
    W, H = 180, 260

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Marvin")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=TK)

        try:
            self.root.wm_attributes("-transparentcolor", TK)
        except Exception:
            pass

        try:
            self.root.attributes("-alpha", cfg.get("opacidade", 1.0))
        except Exception:
            pass

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        sx = cfg.get("pos_x") or sw - self.W - 20
        sy = cfg.get("pos_y") or sh - self.H - 60
        self.root.geometry(f"{self.W}x{self.H}+{sx}+{sy}")

        self.cv = tk.Canvas(self.root, width=self.W, height=self.H,
                             bg=TK, highlightthickness=0)
        self.cv.pack()

        # Estado
        self.t               = 0.0
        self.state           = "thinking"
        self.bubble          = ""
        self.b_timer         = 0
        self._reminder_queue = []
        self._panel_open     = False
        self._dragging       = False
        self._drag_dist      = 0
        self._dx = self._dy  = 0
        
        

        # Frases idle
        self._idle_interval  = 45000
        self._schedule_idle()

        # Eventos
        self.cv.bind("<ButtonPress-1>",   self._drag_start)
        self.cv.bind("<B1-Motion>",       self._drag_move)
        self.cv.bind("<ButtonRelease-1>", self._drag_end)
        self.cv.bind("<Button-3>",        self._show_menu)
    
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind_all("<Control-Shift-N>",
                            lambda e: NewTaskWindow(self.root, self))

        # Menu contextual — textvariable NAO e suportado em add_command,
        # por isso usamos label fixo e atualizamos com entryconfig pelo indice
        self.ctx = tk.Menu(self.root, tearoff=0,
                            bg=C["panel"], fg=C["accent"],
                            activebackground=C["border"],
                            activeforeground=C["text"],
                            font=("Consolas", 9), bd=0)
        self.ctx.add_command(
            label="+ Nova Tarefa  [Ctrl+Shift+N]",
            command=lambda: NewTaskWindow(self.root, self))          # indice 0
        self.ctx.add_command(
            label="Ver Tarefas",
            command=lambda: TaskWindow(self.root, self))             # indice 1
        self.ctx.add_separator()                                     # indice 2
        self.ctx.add_command(
            label=self._np_label(),
            command=self._toggle_np)                                 # indice 3
        self.ctx.add_separator()                                     # indice 4
        self.ctx.add_command(
            label="Configuracoes",
            command=lambda: SettingsWindow(self.root, self))         # indice 5
        self.ctx.add_separator()                                     # indice 6
        self.ctx.add_command(
            label="Fechar Marvin",
            command=self._on_close)                                  # indice 7

        self._animate()
        self._start_reminders()

        threading.Thread(target=db_limpar_antigas, daemon=True).start()
        self.root.after(900, self._saudacao_inicial)

    # ── Nao Perturbe ─────────────────────────────────────────────────────────

    def _np_label(self):
        if cfg.get("nao_perturbe"):
            return "Desativar Nao Perturbe"
        return "Ativar Nao Perturbe"

    def _toggle_np(self):
        cfg["nao_perturbe"] = not cfg.get("nao_perturbe", False)
        save_cfg()
        # Atualiza o label do item de menu pelo indice (3)
        self.ctx.entryconfig(3, label=self._np_label())
        estado = "ativado" if cfg["nao_perturbe"] else "desativado"
        self.say(f"Nao Perturbe {estado}.", "talking", 2500)

    # ── Saudacao ──────────────────────────────────────────────────────────────

    def _saudacao_inicial(self):
        self.state = "idle"
        rows = db_listar()
        n    = len([r for r in rows if not r[6]])
        self.say(_frase_saudacao(n), "talking", 5000)

    # ── Idle aleatorio ────────────────────────────────────────────────────────

    def _schedule_idle(self):
        self.root.after(self._idle_interval, self._idle_msg)

    def _idle_msg(self):
        if self.state == "idle" and not self.bubble:
            self.say(random.choice(_IDLE_MSGS), "talking", 10000)
        self._schedule_idle()

    # ── Fala ──────────────────────────────────────────────────────────────────

    def say(self, text, state="talking", duration=4000):
        self.bubble  = text
        self.state   = state
        self.b_timer = duration

    # ── Fila de lembretes ─────────────────────────────────────────────────────

    @property
    def reminded_task(self):
        return self._reminder_queue[0] if self._reminder_queue else None

    def complete_task(self):
        if self._reminder_queue:
            db_concluir(self._reminder_queue[0][0])
        self._next_reminder()
        streak = db_streak_hoje()
        msg = "Tarefa concluida!"
        if streak and streak % 5 == 0:
            msg += f"  {streak} hoje!"
        self.say(msg, "talking", 3000)

    def _next_reminder(self):
        if self._reminder_queue:
            self._reminder_queue.pop(0)
        if self._reminder_queue:
            nxt = self._reminder_queue[0]
            self.state   = "alert"
            self.b_timer = 0
            self.bubble  = f"Hora de: {nxt[1]}"
        else:
            self.state  = "idle"
            self.bubble = ""

    # ── Animacao ──────────────────────────────────────────────────────────────

    def _animate(self):
        self.t += 0.05
        if self.b_timer > 0:
            self.b_timer -= 50
            if self.b_timer <= 0:
                self.bubble = ""
                if not self._reminder_queue:
                    self.state = "idle"

        draw_cat(self.cv, self.t, self.state, self.W, self.H)

        if self.bubble:
            bob   = math.sin(self.t * 1.4) * 3
            top_y = int(self.H - CAT_ROWS * PX - 8 + bob)
            draw_bubble(self.cv, self.t, self.W // 2,
                         top_y, self.bubble, self.W)

        self.root.after(50, self._animate)

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _drag_start(self, e):
        self._dx, self._dy = e.x, e.y
        self._drag_dist    = 0

    def _drag_move(self, e):
        dx = e.x - self._dx
        dy = e.y - self._dy
        self._drag_dist += abs(dx) + abs(dy)
        if self._drag_dist > 4:
            self._dragging = True
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _drag_end(self, e):
        cfg["pos_x"] = self.root.winfo_x()
        cfg["pos_y"] = self.root.winfo_y()
        save_cfg()
        if not self._dragging:
            self._on_click()
        self._dragging  = False
        self._drag_dist = 0

    def _on_click(self):
        if self._panel_open:
            return
        self._panel_open = True
        mode = "alert" if self._reminder_queue else "idle"
        p    = InteractionPanel(self.root, self, mode=mode)
        p.win.bind("<Destroy>",
                    lambda e: setattr(self, "_panel_open", False))

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _show_menu(self, e):
        try:
            self.ctx.tk_popup(e.x_root, e.y_root)
        finally:
            self.ctx.grab_release()

 

    # ── Lembretes ─────────────────────────────────────────────────────────────

    def _start_reminders(self):
        def loop():
            while True:
                time.sleep(15)
                now   = datetime.datetime.now()
                today = now.strftime("%Y-%m-%d")
                try:
                    rows = db_listar(apenas_pendentes=True)
                except Exception:
                    continue
                for row in rows:
                    tid, texto, desc, data, hora, rep, conc, lemb = row
                    if lemb:
                        continue
                    hora_s = hora[:5]
                    try:
                        task_dt = datetime.datetime.strptime(
                            f"{data} {hora_s}", "%Y-%m-%d %H:%M")
                    except ValueError:
                        continue
                    diff = (now - task_dt).total_seconds()
                    if 0 <= diff < 90:
                        if self._should_remind(rep, data, now, today):
                            self.root.after(0, lambda r=row: self._enqueue(r))
        threading.Thread(target=loop, daemon=True).start()

    def _should_remind(self, rep, data, now, today):
        if rep == "Nunca":
            return data == today
        if rep == "Todo dia":
            return True
        if rep == "Toda semana":
            try:
                return (datetime.date.fromisoformat(data).weekday()
                        == now.weekday())
            except Exception:
                return False
        if rep == "Seg/Qua/Sex":
            return now.weekday() in (0, 2, 4)
        if rep == "Seg a Sex":
            return now.weekday() < 5
        if rep == "Fins de semana":
            return now.weekday() >= 5
        return False

    def _enqueue(self, row):
        tid = row[0]
        rep = row[5]
        if any(r[0] == tid for r in self._reminder_queue):
            return
        db_marcar_lembrado(tid)
        if rep != "Nunca":
            self.root.after(95000, lambda i=tid: db_reset_lembrado(i))

        self._reminder_queue.append(row)

        if cfg.get("nao_perturbe"):
            NotifPopup(self.root, row[1], row[2], duration=5000)
            return

        if cfg.get("som", True):
            threading.Thread(target=_beep, daemon=True).start()

        NotifPopup(self.root, row[1], row[2])
        if len(self._reminder_queue) == 1:
            self.state   = "alert"
            self.b_timer = 0
            self.bubble  = f"Hora de: {row[1]}"

    # ── Fechar ────────────────────────────────────────────────────────────────

    def _on_close(self):
        cfg["pos_x"] = self.root.winfo_x()
        cfg["pos_y"] = self.root.winfo_y()
        save_cfg()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# =============================================================================
if __name__ == "__main__":
    MarvinCompanion().run()