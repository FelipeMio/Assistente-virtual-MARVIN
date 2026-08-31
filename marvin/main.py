import tkinter as tk
import customtkinter as ctk
import threading, math, time, datetime, random, sys, textwrap, os, queue
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk

try:
    import pystray
except ImportError:
    pystray = None


# ============================================================
# WIN32
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
        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD),
            ]

from .config import load_cfg, save_cfg
from .theme import get_palette, get_modern_palette

from .extension_loader import carregar_extensoes
from .checklist import abrir_checklist
from .ui.home import abrir_home

from marvin.database import (
    DB_F,
    db_listar,
    db_listar_com_prioridade,
    db_criar,
    db_concluir,
    db_desconcluir,
    db_excluir,
    db_alterar,
    db_obter,
    db_marcar_lembrado,
    db_reset_lembrado,
    db_adiar,
    db_streak_hoje,
    db_limpar_antigas,
)



# CONFIGURAÇÃO

cfg = load_cfg()


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


#  INICIALIZACAO COM O WINDOWS


def _startup_file():
    """
    Retorna o arquivo usado para iniciar
    o MARVIN automaticamente com o Windows.
    """
    if sys.platform != "win32":
        return None

    appdata = os.environ.get("APPDATA")

    if not appdata:
        return None

    return (
        Path(appdata)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
        / "MARVIN.cmd"
    )


def _startup_enabled():
    arquivo = _startup_file()

    return bool(
        arquivo
        and arquivo.exists()
    )


def _set_startup_enabled(enabled):
    """
    Cria ou remove o atalho de inicializacao
    automatica do MARVIN.
    """
    arquivo = _startup_file()

    if arquivo is None:
        return False

    try:
        if enabled:
            # Estrutura:
            # projeto/
            #   marvin/
            #       main.py
            projeto = (
                Path(__file__)
                .resolve()
                .parent
                .parent
            )

            python_exe = Path(sys.executable)

            # Usa pythonw para nao abrir o terminal
            # quando o Windows iniciar o MARVIN.
            pythonw = python_exe.with_name(
                "pythonw.exe"
            )

            if not pythonw.exists():
                pythonw = python_exe

            conteudo = (
                "@echo off\n"
                f'cd /d "{projeto}"\n'
                f'start "" "{pythonw}" -m marvin.main\n'
            )

            arquivo.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            arquivo.write_text(
                conteudo,
                encoding="utf-8"
            )

        else:
            if arquivo.exists():
                arquivo.unlink()

        return True

    except Exception as exc:
        print(
            f"[MARVIN] Erro ao configurar inicio com Windows: {exc}"
        )
        return False


#  PALETA

TK = "#010203"  # cor de transparencia Windows

C = get_palette(
    cfg.get(
        "tema",
        "escuro"
    )
)

# ============================================================
# [LEGADO] PIXEL ART ANTIGA DO MARVIN
#
# Este sistema nao e mais utilizado.
# O MARVIN atual usa sprites PNG em assets/marvin/.
# Mantido apenas como referencia.
# ============================================================
#
# #  PIXEL ART DO MARVIN
#
# _PAL = {
#     " ": None,
#     "#": "#000000",
#     "D": "#2e2f34",
#     "B": "#2c334d",
#     "W": "#f9f6e9",
#     "R": "#9f2929",
#     "P": "#d77c78",
#     "G": "#a0aab1",
# }
#
# GATO = [
#     "     ##           ##    ",
#     "    #DD#         #DDD   ",
#     "    #PDD#       #DPPD   ",
#     "    #PPDD#######DPPPD   ",
#     "    #PPPDDDDDDDDPPPPD   ",
#     "    #PPDDDDDDDDDDPPPD   ",
#     "    #PDDDDDDDDDDDDDPD   ",
#     "    #DDDDDDWGDDDDDDD#   ",
#     "    #DDDDD#WGDDDDDDDD   ",
#     "   #DDD#DDWWWD#DDDDDDG  ",
#     "WWWBGDDG#DWWWDG#DDDGGGWW",
#     "WWW#DDDDDWWWWBDDDDDDDBWW",
#     "   #GDDDWWGPWWWDDDDGGB  ",
#     " GGGDDDWWWGWWWWWWDDDGGG ",
#     "    #WWWWWG##WWWWWW #   ",
#     "     #WWWWWWWWWWWWW#    ",
#     "      #WWWWWWWWWW##     ",
#     "      ###########B##    ",
#     "     #BB#WRRG #BBBBB#   ",
#     "    #BBBBBGRG #BBBBB#   ",
#     "    #BBBBBGRGBBBBBBBB#  ",
#     "   #BBBBBBGRGBBBBBBBB#  ",
#     "   #B#BBBDRRRBBBBB#BBB# ",
#     "  #BB#BBBBDRRBBBBB#BBB# ",
#     "  #BB#BBBBDDBBBBBB#BBB# ",
#     "  #BB#BBBBBBBBBBBB#BBB# ",
#     "  #BB#BBBBBBBBBBBB#BBB# ",
#     "  ####BBBBBBBBBBBB##### ",
#     "  #WW#BBBBBBBBBBBB#GWW# ",
#     "  W###BBBBBBBBBBBBB###W ",
#     "     ###############    ",
#     "      #BBBBBBBBBBBB#    ",
#     "      #BBBBBBBBBBBB#    ",
#     "      #BBBD##DBBBB#     ",
#     "       #BBDW DBBBB#     ",
#     "       #BBDW  #BBB#     ",
#     "       ####W  #####     ",
#     "     G#WWWGGGG#WWWW#G   ",
#     "    GGBBBBBGGGG#BBBBGG  ",
#     "      GGGGGGGGGGGGGG    ",
# ]
#
# CAT_COLS = 24
# CAT_ROWS = 40
# PX       = 4
#
#
# def _cor_pixel(ch, row, col, t, state, blink):
#     if blink and 7 <= row <= 10 and ch in ("#", "W"):
#         if (7 <= col <= 8) or (13 <= col <= 14):
#             return _PAL["D"]
#     if ch == "R" and state == "alert":
#         p  = abs(math.sin(t * 6))
#         rv = int(0x9f + p * (0xff - 0x9f))
#         gv = int(0x29 * (1 - p) + 0xaa * p)
#         bv = int(0x29 * (1 - p))
#         return f"#{rv:02x}{gv:02x}{bv:02x}"
#     return _PAL.get(ch)
#
#
# def draw_cat(cv, t, state, W, H):
#     cv.delete("all")
#     bob     = math.sin(t * 1.4) * 3
#     total_w = CAT_COLS * PX
#     total_h = CAT_ROWS * PX
#     ox      = (W - total_w) // 2
#     oy      = int(H - total_h - 8 + bob)
#
#
#     # Halo alert
#     if state == "alert":
#         p    = abs(math.sin(t * 4))
#         rv   = int(160 + p * 80)
#         gv   = int(60  + p * 60)
#         hcol = f"#{rv:02x}{gv:02x}00"
#         for dr in (3, 7, 12):
#             cv.create_rectangle(ox - dr, oy - dr,
#                                  ox + total_w + dr, oy + total_h + dr,
#                                  fill="", outline=hcol, width=1)
#
#     # Halo thinking
#     if state == "thinking":
#         p    = abs(math.sin(t * 2))
#         bv   = int(80 + p * 80)
#         hcol = f"#00{bv:02x}ff"
#         for dr in (3, 7):
#             cv.create_rectangle(ox - dr, oy - dr,
#                                  ox + total_w + dr, oy + total_h + dr,
#                                  fill="", outline=hcol, width=1)
#
#     arm_shift = int(math.sin(t * 7) * 9) if state == "alert" else 0
#     blink     = (int(t * 2.0) % 100 < 4)
#
#     for row_i, linha in enumerate(GATO):
#         for col_i, ch in enumerate(linha):
#             if ch == " ":
#                 continue
#             cor = _cor_pixel(ch, row_i, col_i, t, state, blink)
#             if cor is None:
#                 continue
#             dy = arm_shift if (state == "alert"
#                                and 20 <= row_i <= 28
#                                and 20 <= col_i <= 23) else 0
#             x0 = ox + col_i * PX
#             y0 = oy + row_i * PX + dy
#             cv.create_rectangle(x0, y0, x0 + PX, y0 + PX,
#                                  fill=cor, outline="")
#
#

def _bubble_layout(text, W, cx, top_y, mode="normal"):
    """Calcula toda a geometria visual e clicavel do balao."""

    wrapped = textwrap.wrap(
        text,
        width=26
    )[:4]

    if not wrapped:
        return None

    line_h = 15
    py = 9

    if mode == "alert":
        button_h = 34

    elif mode == "snooze":
        button_h = 54

    else:
        button_h = 0

    bw = max(
        1,
        W - 12
    )

    bh = (
        len(wrapped) * line_h
        + py * 2
        + button_h
    )

    bx = max(
        6,
        cx - bw // 2
    )

    by = max(
        6,
        top_y - bh - 16
    )

    layout = {
        "wrapped": wrapped,
        "line_h": line_h,
        "py": py,
        "bw": bw,
        "bh": bh,
        "bx": bx,
        "by": by,
        "button_y": None,
    }

    if mode in (
        "alert",
        "snooze",
    ):
        layout["button_y"] = (
            by
            + py
            + len(wrapped) * line_h
            + 5
        )

    if mode == "alert":
        layout["complete_x"] = (
            bx + bw // 3
        )

        layout["snooze_x"] = (
            bx + (bw * 2) // 3
        )

    elif mode == "snooze":
        spacing = bw / 4

        layout["option_x"] = {
            value: (
                bx
                + spacing * i
                + spacing / 2
            )
            for i, value in enumerate(
                ("5", "15", "30", "60")
            )
        }

        layout["back_y"] = (
            layout["button_y"] + 31
        )

    return layout


def draw_bubble(cv, t, cx, top_y, text, W, mode="normal", hover=None):

    layout = _bubble_layout(
        text,
        W,
        cx,
        top_y,
        mode
    )

    if layout is None:
        return

    wrapped = layout["wrapped"]
    line_h = layout["line_h"]
    py = layout["py"]
    bw = layout["bw"]
    bh = layout["bh"]
    bx = layout["bx"]
    by = layout["by"]

    # ---------------------------------------------------------
    # SOMBRA
    # ---------------------------------------------------------
    cv.create_rectangle(
        bx + 2, by + 2,
        bx + bw + 2, by + bh + 2,
        fill="#060c14",
        outline=""
    )

    # ---------------------------------------------------------
    # BALÃO
    # ---------------------------------------------------------
    cv.create_rectangle(
        bx, by,
        bx + bw, by + bh,
        fill=C["bub_bg"],
        outline=C["bub_bd"],
        width=2
    )

    # ---------------------------------------------------------
    # PONTA DO BALÃO
    # ---------------------------------------------------------
    tip = min(
        max(cx, bx + 16),
        bx + bw - 16
    )

    cv.create_polygon(
        [
            tip - 7, by + bh,
            tip + 7, by + bh,
            tip, top_y - 2
        ],
        fill=C["bub_bg"],
        outline=C["bub_bd"]
    )

    cv.create_line(
        bx + 2, by + bh,
        tip - 7, by + bh,
        fill=C["bub_bd"],
        width=2
    )

    cv.create_line(
        tip + 7, by + bh,
        bx + bw - 2, by + bh,
        fill=C["bub_bd"],
        width=2
    )

    # ---------------------------------------------------------
    # TEXTO
    # ---------------------------------------------------------
    text_y = by + py

    for i, line in enumerate(wrapped):

        cv.create_text(
            bx + bw // 2,
            text_y + i * line_h + line_h // 2,
            text=line,
            fill=C["text"],
            font=("Consolas", 8),
            anchor="center"
        )

    # =========================================================
    # ALERTA
    # =========================================================
    if mode == "alert":

        button_y = layout["button_y"]

        # Posicoes vindas da mesma geometria
        # usada para detectar os cliques.
        complete_x = layout["complete_x"]
        snooze_x = layout["snooze_x"]

        # -------------------------
        # CONCLUIR
        # -------------------------
        complete_active = hover == "complete"

        cv.create_oval(
            complete_x - 11,
            button_y,
            complete_x + 11,
            button_y + 22,
            fill=C["green"] if complete_active else C["panel"],
            outline=C["green"],
            width=2
        )

        cv.create_text(
            complete_x,
            button_y + 11,
            text="✓",
            fill="#ffffff",
            font=("Consolas", 11, "bold")
        )

        cv.create_text(
            complete_x,
            button_y + 29,
            text="concluir",
            fill=C["dim"],
            font=("Consolas", 7)
        )

        # -------------------------
        # ADIAR
        # -------------------------
        snooze_active = hover == "snooze"

        cv.create_oval(
            snooze_x - 11,
            button_y,
            snooze_x + 11,
            button_y + 22,
            fill=C["accent"] if snooze_active else C["panel"],
            outline=C["accent"],
            width=2
        )

        cv.create_text(
            snooze_x,
            button_y + 11,
            text="⏰",
            fill="#ffffff",
            font=("Segoe UI Symbol", 9)
        )

        cv.create_text(
            snooze_x,
            button_y + 29,
            text="adiar",
            fill=C["dim"],
            font=("Consolas", 7)
        )

    # =========================================================
    # MENU DE ADIAMENTO
    # =========================================================
    elif mode == "snooze":

        button_y = layout["button_y"]

        options = [
            ("5", "5m"),
            ("15", "15m"),
            ("30", "30m"),
            ("60", "1h"),
        ]

        for value, label in options:

            x = layout["option_x"][value]

            active = hover == value

            cv.create_oval(
                x - 14,
                button_y,
                x + 14,
                button_y + 24,
                fill=C["accent"] if active else C["panel"],
                outline=C["accent"],
                width=1
            )

            cv.create_text(
                x,
                button_y + 12,
                text=label,
                fill="#ffffff",
                font=("Consolas", 7, "bold")
            )

        # -------------------------
        # VOLTAR
        # -------------------------
        back_y = layout["back_y"]

        active = hover == "back"

        cv.create_text(
            bx + bw // 2,
            back_y,
            text="↩ voltar",
            fill=C["accent"] if active else C["dim"],
            font=("Consolas", 7, "bold")
        )

#  FRASES IDLE

_IDLE_MSGS = [
    
    "Clique com botao esquerdo para o menu.",
    "Clique com botao direito para o menu.",
  
    
]

def _frases_idle_ativas():
    """
    Retorna as frases personalizadas do MARVIN.
    Se nao houver nenhuma valida, usa as frases padrao.
    """
    frases = cfg.get("frases_idle", [])

    if isinstance(frases, list):
        frases = [
            str(frase).strip()
            for frase in frases
            if str(frase).strip()
        ]

    if frases:
        return frases

    return _IDLE_MSGS


def _frase_saudacao(n):
    hora = datetime.datetime.now().hour
    saud = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
    if n:
        return f"{saud}! {n} tarefa(s) pendente(s)."
    return f"{saud}! Sem tarefas pendentes."

#  HELPERS DE UI

REPEAT_OPTS = ["Nunca", "Todo dia", "Toda semana",
               "Seg/Qua/Sex", "Seg a Sex", "Fins de semana"]

PRIORITY_OPTS = [
    "Baixa",
    "Normal",
    "Alta",
]


def _make_win(parent, title, w, h, resizable=False):
    win = tk.Toplevel(parent)
    win.title(f"Marvin - {title}")
    win.configure(bg=C["win_bg"])
    win.geometry(f"{w}x{h}")
    win.attributes("-topmost", True)
    win.resizable(resizable, resizable)
    return win


def _position_near_marvin(win, companion):
    """Posiciona uma janela no mesmo monitor e perto do MARVIN."""

    root = companion.root

    win.update_idletasks()

    ww = win.winfo_width()
    wh = win.winfo_height()

    rx = root.winfo_x()
    ry = root.winfo_y()
    rw = companion.W
    rh = companion.H

    # Fallback para monitor principal
    mon_left = 0
    mon_top = 0
    mon_right = root.winfo_screenwidth()
    mon_bottom = root.winfo_screenheight()

    if sys.platform == "win32":
        try:


            user32 = ctypes.windll.user32

            monitor = user32.MonitorFromWindow(
                root.winfo_id(),
                2
            )

            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)

            if user32.GetMonitorInfoW(
                monitor,
                ctypes.byref(info)
            ):
                mon_left = info.rcWork.left
                mon_top = info.rcWork.top
                mon_right = info.rcWork.right
                mon_bottom = info.rcWork.bottom

        except Exception:
            pass

    gap = 12

    # Tenta abrir do lado esquerdo
    if rx - ww - gap >= mon_left:
        px = rx - ww - gap

    # Senao abre do lado direito
    elif rx + rw + gap + ww <= mon_right:
        px = rx + rw + gap

    # Ultimo recurso: mantem dentro do monitor
    else:
        px = max(
            mon_left,
            min(
                rx + rw + gap,
                mon_right - ww
            )
        )

    # Centraliza verticalmente em relacao ao MARVIN
    py = ry + (rh - wh) // 2

    py = max(
        mon_top,
        min(
            py,
            mon_bottom - wh
        )
    )

    win.geometry(
        f"+{px}+{py}"
    )

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


def _priority_menu(parent, var):
    opt = tk.OptionMenu(
        parent,
        var,
        *PRIORITY_OPTS
    )

    opt.config(
        bg=C["panel"],
        fg=C["text"],
        activebackground=C["border"],
        activeforeground=C["text"],
        font=("Consolas", 9),
        highlightthickness=0,
        bd=0
    )

    opt["menu"].config(
        bg=C["panel"],
        fg=C["text"],
        activebackground=C["border"],
        activeforeground=C["text"],
        font=("Consolas", 9)
    )

    opt.pack(
        fill="x",
        ipady=4
    )

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

def _bind_auto_time(entry, var):
    """
    Formata horario enquanto o usuario digita.

    Exemplos:
        14 + 40 -> 14:40
        1830    -> 18:30

    Mantem o cursor no final para evitar
    14:40 virar 14:04.
    """

    controle = {
        "alterando": False
    }

    def formatar(event=None):
        if controle["alterando"]:
            return

        atual = var.get()

        digitos = "".join(
            ch
            for ch in atual
            if ch.isdigit()
        )[:4]

        if len(digitos) <= 2:
            novo = digitos
        else:
            novo = (
                digitos[:2]
                + ":"
                + digitos[2:]
            )

        if novo != atual:
            controle["alterando"] = True

            try:
                var.set(novo)
            finally:
                controle["alterando"] = False

        # O ponto principal da correcao:
        # depois da formatacao, mantem o cursor
        # depois do ultimo caractere.
        try:
            entry.icursor("end")
        except Exception:
            pass

    # Formata somente depois da tecla ser processada.
    entry.bind(
        "<KeyRelease>",
        formatar,
        add="+"
    )

    # Tambem funciona ao colar um horario.
    entry.bind(
        "<<Paste>>",
        lambda e: entry.after_idle(
            formatar
        ),
        add="+"
    )

    # Garante formato correto ao sair do campo.
    entry.bind(
        "<FocusOut>",
        formatar,
        add="+"
    )




#  JANELA: NOVA TAREFA

class NewTaskWindow:

    WIDTH = 390
    HEIGHT = 590

    def __init__(
        self,
        parent,
        companion,
        prefill="",
    ):
        self.comp = companion
        self.parent = parent

        self.tema = cfg.get(
            "tema",
            "escuro",
        )

        self.colors = get_modern_palette(self.tema, "task_form")

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
            False,
            False,
        )

        self.win.overrideredirect(
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self.win.grab_set()

        self._drag_x = 0
        self._drag_y = 0

        self._build(
            prefill
        )

        _position_near_marvin(
            self.win,
            self.comp
        )

        self.win.bind(
            "<Escape>",
            lambda e:
                self._close()
        )

        self.win.after(
            80,
            self._focus_title
        )


    # ========================================================
    # JANELA
    # ========================================================

    def _close(self):
        try:
            self.win.grab_release()
        except Exception:
            pass

        try:
            self.win.destroy()
        except Exception:
            pass


    def _focus_title(self):
        try:
            self.e_txt.focus()
        except Exception:
            pass


    def _drag_start(
        self,
        event,
    ):
        self._drag_x = (
            event.x_root
            - self.win.winfo_x()
        )

        self._drag_y = (
            event.y_root
            - self.win.winfo_y()
        )


    def _drag_move(
        self,
        event,
    ):
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
    # HELPERS
    # ========================================================

    def _label(
        self,
        parent,
        text,
        required=False,
    ):
        texto = text

        if required:
            texto += " *"

        label = ctk.CTkLabel(
            parent,
            text=texto.upper(),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),
        )

        label.pack(
            fill="x",
            pady=(0, 5),
        )

        return label


    def _entry(
        self,
        parent,
        variable,
        placeholder="",
    ):
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,

            height=36,

            corner_radius=7,

            fg_color=self.colors["input"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            placeholder_text=placeholder,
            placeholder_text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
        )

        entry.pack(
            fill="x",
        )

        return entry


    def _divider(
        self,
        parent,
    ):
        ctk.CTkFrame(
            parent,
            height=1,
            fg_color=self.colors["border"],
            corner_radius=0,
        ).pack(
            fill="x",
        )


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(
        self,
        prefill,
    ):
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


        marca = ctk.CTkFrame(
            titlebar,
            width=21,
            height=21,
            corner_radius=6,
            fg_color=self.colors["accent"],
        )

        marca.pack(
            side="left",
            padx=(14, 0),
        )

        marca.pack_propagate(
            False
        )

        ctk.CTkLabel(
            marca,
            text="",
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=9,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )


        ctk.CTkLabel(
            titlebar,
            text="NOVA TAREFA",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
        ).pack(
            side="left",
            padx=(8, 0),
        )


        ctk.CTkButton(
            titlebar,

            text="×",

            width=28,
            height=28,

            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["input_hover"],

            text_color=self.colors["dim"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

            command=self._close,

        ).pack(
            side="right",
            padx=10,
        )


        self._divider(
            shell
        )


        # ====================================================
        # BODY
        # ====================================================

        body = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["dim"],
        )

        body.pack(
            fill="both",
            expand=True,
            padx=(20, 8),
            pady=(16, 8),
        )


        ctk.CTkLabel(
            body,

            text="Nova tarefa",

            text_color=self.colors["text"],

            anchor="w",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),

        ).pack(
            fill="x",
            pady=(0, 15),
        )


        # ====================================================
        # TITULO
        # ====================================================

        self._label(
            body,
            "Título",
            True,
        )

        self.v_txt = tk.StringVar(
            value=prefill
        )

        self.e_txt = self._entry(
            body,
            self.v_txt,
            "Nome da tarefa",
        )


        # ====================================================
        # DESCRICAO
        # ====================================================

        desc_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        desc_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            desc_wrap,
            "Descrição",
        )


        self.desc_box = ctk.CTkTextbox(
            desc_wrap,

            height=76,

            corner_radius=7,

            fg_color=self.colors["input"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            wrap="word",
        )

        self.desc_box.pack(
            fill="x",
        )


        # ====================================================
        # DATA / HORA
        # ====================================================

        date_row = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        date_row.pack(
            fill="x",
            pady=(13, 0),
        )

        date_row.grid_columnconfigure(
            0,
            weight=1,
        )

        date_row.grid_columnconfigure(
            1,
            weight=1,
        )


        data_frame = ctk.CTkFrame(
            date_row,
            fg_color="transparent",
        )

        data_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
        )


        hora_frame = ctk.CTkFrame(
            date_row,
            fg_color="transparent",
        )

        hora_frame.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
        )


        self._label(
            data_frame,
            "Data",
            True,
        )

        self._label(
            hora_frame,
            "Horário",
            True,
        )


        proximo_minuto = (
            datetime.datetime.now()
            .replace(
                second=0,
                microsecond=0,
            )
            + datetime.timedelta(
                minutes=1
            )
        )


        self.v_data = tk.StringVar(
            value=(
                proximo_minuto
                .strftime(
                    "%d/%m/%Y"
                )
            )
        )

        self.v_hora = tk.StringVar(
            value=(
                proximo_minuto
                .strftime(
                    "%H:%M"
                )
            )
        )


        self.e_data = self._entry(
            data_frame,
            self.v_data,
        )

        self.e_hora = self._entry(
            hora_frame,
            self.v_hora,
        )


        _bind_auto_time(
            self.e_hora,
            self.v_hora
        )


        self.v_data.trace_add(
            "write",
            self._validate_live
        )

        self.v_hora.trace_add(
            "write",
            self._validate_live
        )


        # ====================================================
        # REPETICAO
        # ====================================================

        repeat_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        repeat_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            repeat_wrap,
            "Repetição",
        )


        self.v_rep = tk.StringVar(
            value=REPEAT_OPTS[0]
        )


        self.repeat_combo = ctk.CTkComboBox(
            repeat_wrap,

            variable=self.v_rep,

            values=list(
                REPEAT_OPTS
            ),

            height=36,

            corner_radius=7,

            fg_color=self.colors["input"],
            button_color=self.colors["input"],
            button_hover_color=self.colors["input_hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            dropdown_fg_color=self.colors["card"],
            dropdown_hover_color=self.colors["input_hover"],
            dropdown_text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            dropdown_font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            state="readonly",
        )

        self.repeat_combo.pack(
            fill="x",
        )


        # ====================================================
        # PRIORIDADE
        # ====================================================

        priority_wrap = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        priority_wrap.pack(
            fill="x",
            pady=(13, 0),
        )


        self._label(
            priority_wrap,
            "Prioridade",
        )


        priority_row = ctk.CTkFrame(
            priority_wrap,
            fg_color="transparent",
        )

        priority_row.pack(
            fill="x",
        )

        # As tres colunas usam exatamente a mesma largura.
        for coluna in range(4):
            priority_row.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="prioridade",
            )


        self.v_prioridade = tk.StringVar(
            value="Nenhuma"
        )

        self.priority_buttons = {}


        for coluna, (texto, prioridade) in enumerate((
            ("Alta", "Alta"),
            ("Média", "Normal"),
            ("Baixa", "Baixa"),
            ("Nenhuma", "Nenhuma"),
        )):
            button = ctk.CTkButton(
                priority_row,

                text=texto,

                height=46,

                corner_radius=7,

                fg_color="transparent",

                hover_color=self.colors["input_hover"],

                border_width=1,
                border_color=self.colors["border"],

                text_color=self.colors["dim"],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),

                command=lambda p=prioridade:
                    self._set_priority(
                        p
                    ),
            )

            button.grid(
                row=0,
                column=coluna,
                sticky="ew",
                padx=(
                    (0, 3)
                    if coluna == 0
                    else (
                        (3, 0)
                        if coluna == 3
                        else (3, 3)
                    )
                ),
            )

            self.priority_buttons[
                prioridade
            ] = button


        self._set_priority(
            "Nenhuma"
        )


        # ====================================================
        # ERRO
        # ====================================================

        self.v_err = tk.StringVar()


        self.error_label = ctk.CTkLabel(
            body,

            textvariable=self.v_err,

            text_color=self.colors["error"],

            anchor="w",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        )

        self.error_label.pack(
            fill="x",
            pady=(7, 0),
        )


        # ====================================================
        # FOOTER
        # ====================================================

        footer = ctk.CTkFrame(
            shell,
            fg_color=self.colors["card"],
        )

        # O footer precisa ser reservado antes da area expansivel.
        # Reempacotamos o body depois dele para garantir que
        # Salvar/Cancelar nunca saiam da janela.
        footer.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=(4, 12),
        )

        body.pack_forget()

        body.pack(
            side="top",
            fill="both",
            expand=True,
            padx=(20, 8),
            pady=(16, 8),
        )


        ctk.CTkButton(
            footer,

            text="Salvar",

            height=36,

            corner_radius=7,

            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],

            text_color="#FFFFFF",

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),

            command=self._salvar,

        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )


        ctk.CTkButton(
            footer,

            text="Cancelar",

            height=36,

            corner_radius=7,

            fg_color="transparent",
            hover_color=self.colors["input_hover"],

            border_width=1,
            border_color=self.colors["border"],

            text_color=self.colors["text"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),

            command=self._close,

        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )


    # ========================================================
    # PRIORIDADE
    # ========================================================

    def _set_priority(
        self,
        prioridade,
    ):
        self.v_prioridade.set(
            prioridade
        )


        for nome, button in (
            self.priority_buttons.items()
        ):

            if nome != prioridade:
                button.configure(
                    fg_color="transparent",
                    border_color=self.colors["border"],
                    text_color=self.colors["dim"],
                )

                continue


            if nome == "Alta":
                button.configure(
                    fg_color=self.colors["high_bg"],
                    border_color=self.colors["high_fg"],
                    text_color=self.colors["high_fg"],
                )

            elif nome == "Normal":
                button.configure(
                    fg_color=self.colors["normal_bg"],
                    border_color=self.colors["normal_fg"],
                    text_color=self.colors["normal_fg"],
                )

            elif nome == "Baixa":
                button.configure(
                    fg_color=self.colors["low_bg"],
                    border_color=self.colors["low_fg"],
                    text_color=self.colors["low_fg"],
                )

            else:
                button.configure(
                    fg_color=self.colors["none_bg"],
                    border_color=self.colors["none_fg"],
                    text_color=self.colors["none_fg"],
                )


    # ========================================================
    # VALIDACAO
    # ========================================================

    def _validate_live(
        self,
        *_,
    ):
        d_ok = (
            _validate_date(
                self.v_data.get()
            )
            is not None
        )

        h_ok = (
            _validate_time(
                self.v_hora.get()
            )
            is not None
        )


        self.e_data.configure(
            text_color=(
                self.colors["text"]
                if d_ok
                else self.colors["error"]
            )
        )


        self.e_hora.configure(
            text_color=(
                self.colors["text"]
                if h_ok
                else self.colors["error"]
            )
        )


    # ========================================================
    # SALVAR
    # ========================================================

    def _salvar(
        self,
    ):
        txt = (
            self.v_txt
            .get()
            .strip()
        )


        desc = (
            self.desc_box
            .get(
                "1.0",
                "end"
            )
            .strip()
        )


        data = _validate_date(
            self.v_data.get()
        )

        hora = _validate_time(
            self.v_hora.get()
        )


        if not txt:
            self.v_err.set(
                "Título não pode ser vazio."
            )

            return


        if data is None:
            self.v_err.set(
                "Data inválida. Use DD/MM/AAAA."
            )

            return


        if hora is None:
            self.v_err.set(
                "Horário inválido. Use HH:MM."
            )

            return


        agora = datetime.datetime.now()


        try:
            task_dt = (
                datetime.datetime.strptime(
                    f"{data} {hora}",
                    "%Y-%m-%d %H:%M"
                )
            )

        except ValueError:
            self.v_err.set(
                "Data ou horário inválido."
            )

            return


        if task_dt <= agora:
            self.v_err.set(
                "Escolha um horário a partir do próximo minuto."
            )

            return


        db_criar(
            txt,
            desc,
            data,
            hora,
            self.v_rep.get(),
            self.v_prioridade.get(),
        )


        self.comp.say(
            "Tarefa criada!",
            "talking",
            2000
        )


        self._close()


#  JANELA: LISTA DE TAREFAS

class TaskWindow:

    WIDTH = 470
    HEIGHT = 610

    def __init__(self, parent, companion):
        self.comp = companion
        self.parent = parent

        self.tema = cfg.get(
            "tema",
            "escuro"
        )

        self.colors = get_modern_palette(self.tema, "task_list")

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

        _position_near_marvin(
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
                NewTaskWindow(
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


        rows = db_listar_com_prioridade()


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

            fg_color="transparent",

            corner_radius=0,
        )

        task.pack(
            fill="x",
            pady=(0, 2),
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
            anchor="n",
            padx=(0, 9),
            pady=(7, 0),
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

            width=42,
            height=23,

            fg_color="transparent",
            hover_color=self.colors["hover"],

            text_color=self.colors["accent"],

            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),

            command=lambda i=tid:
                EditTaskWindow(
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

            width=45,
            height=23,

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

        for row in db_listar():

            if row[0] != tid:
                continue


            if row[6]:
                db_desconcluir(
                    tid
                )

            else:
                db_concluir(
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
            db_excluir(
                tid
            )

            self._refresh()



class EditTaskWindow:
    def __init__(self, parent, companion, tid, callback):
        self.comp     = companion
        self.tid      = tid
        self.callback = callback
        row = db_obter(tid)

        if not row:
            messagebox.showwarning(
                "MARVIN",
                (
                    "Esta tarefa nao foi encontrada.\n\n"
                    "Ela pode ter sido excluida ou alterada "
                    "por outra janela."
                ),
                parent=parent
            )
            return

        texto, desc, data, hora, rep, prioridade = row
        self.win = _make_win(parent, "Editar Tarefa", 400, 415)
        self.win.grab_set()
        self._build(
            texto,
            desc,
            data,
            hora,
            rep,
            prioridade
        )
        _position_near_marvin(self.win, self.comp)

    def _build(
        self,
        texto,
        desc,
        data,
        hora,
        rep,
        prioridade
    ):
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
        self.e_hora = _entry(
            Rf,
            self.v_hora,
            width=7
        )

        # Digitar 1830 vira automaticamente 18:30.
        _bind_auto_time(
            self.e_hora,
            self.v_hora
        )

        _lbl(body, "Repeticao")
        self.v_rep = tk.StringVar(value=rep)
        _option_menu(body, self.v_rep)

        _lbl(body, "Prioridade")
        self.v_prioridade = tk.StringVar(
            value=(
                prioridade
                if prioridade in PRIORITY_OPTS
                else "Normal"
            )
        )

        _priority_menu(
            body,
            self.v_prioridade
        )

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
            self.v_err.set(
                "Titulo nao pode ser vazio."
            )
            return

        data_txt = (
            self.v_data
            .get()
            .strip()
        )

        hora = _validate_time(
            self.v_hora.get()
        )

        # A janela legada de edicao historicamente
        # exibe AAAA-MM-DD, enquanto a Nova Tarefa
        # aceita DD/MM/AAAA. Mantemos compatibilidade
        # com os dois formatos.
        data = _validate_date(
            data_txt
        )

        if data is None:
            try:
                data = (
                    datetime.datetime.strptime(
                        data_txt,
                        "%Y-%m-%d"
                    )
                    .strftime(
                        "%Y-%m-%d"
                    )
                )

            except ValueError:
                self.v_err.set(
                    "Data invalida. Use DD/MM/AAAA ou AAAA-MM-DD."
                )
                return

        if hora is None:
            self.v_err.set(
                "Horario invalido. Use HH:MM."
            )
            return

        try:
            task_dt = datetime.datetime.strptime(
                f"{data} {hora}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            self.v_err.set(
                "Data ou horario invalido."
            )
            return

        if task_dt <= datetime.datetime.now():
            self.v_err.set(
                "Escolha um horario a partir do proximo minuto."
            )
            return

        db_alterar(
            self.tid,
            "texto",
            txt
        )

        db_alterar(
            self.tid,
            "descricao",
            self.v_desc.get().strip()
        )

        db_alterar(
            self.tid,
            "data",
            data
        )

        db_alterar(
            self.tid,
            "hora",
            hora
        )

        db_alterar(
            self.tid,
            "recorrencia",
            self.v_rep.get()
        )

        db_alterar(
            self.tid,
            "prioridade",
            self.v_prioridade.get()
        )

        db_alterar(
            self.tid,
            "lembrado",
            0
        )

        self.callback()

        self.comp.say(
            "Tarefa editada!",
            "talking",
            2000
        )

        self.win.destroy()

#  JANELA: FRASES DE ESPERA

class WaitingPhrasesWindow:
    DEFAULTS = [
        "Ei... {tarefa}",
        "Vai fazer ou adiar? {tarefa}",
        "Ainda estou esperando: {tarefa}",
    ]

    def __init__(self, parent, companion):
        self.comp = companion

        self.win = _make_win(
            parent,
            "Frases de espera",
            430,
            310
        )

        self._build()

        _position_near_marvin(
            self.win,
            self.comp
        )


    def _build(self):
        w = self.win

        _header(
            w,
            "Frases de espera"
        )

        body = tk.Frame(
            w,
            bg=C["win_bg"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=12
        )

        tk.Label(
            body,
            text=(
                "Use {tarefa} onde quiser que "
                "apareca o nome da tarefa."
            ),
            bg=C["win_bg"],
            fg=C["dim"],
            font=("Consolas", 8),
            wraplength=380,
            justify="left"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        frases = cfg.get(
            "frases_waiting",
            self.DEFAULTS
        )

        if (
            not isinstance(frases, list)
            or len(frases) < 3
        ):
            frases = list(
                self.DEFAULTS
            )

        self.vars = []

        labels = [
            "Primeira reacao",
            "Segunda reacao",
            "Terceira reacao",
        ]

        for i, label in enumerate(labels):

            tk.Label(
                body,
                text=label,
                bg=C["win_bg"],
                fg=C["dim"],
                font=(
                    "Consolas",
                    8,
                    "bold"
                )
            ).pack(
                anchor="w",
                pady=(5, 2)
            )

            var = tk.StringVar(
                value=str(frases[i])
            )

            self.vars.append(var)

            entry = tk.Entry(
                body,
                textvariable=var,
                bg=C["panel"],
                fg=C["text"],
                insertbackground=C["text"],
                relief="flat",
                bd=0,
                font=("Consolas", 8)
            )

            entry.pack(
                fill="x",
                ipady=6
            )

        botoes = tk.Frame(
            body,
            bg=C["win_bg"]
        )

        botoes.pack(
            anchor="w",
            pady=(14, 0)
        )

        tk.Button(
            botoes,
            text="Salvar",
            bg=C["green"],
            fg=C["win_bg"],
            bd=0,
            padx=14,
            pady=7,
            font=(
                "Consolas",
                9,
                "bold"
            ),
            cursor="hand2",
            activebackground=C["accent"],
            command=self._salvar
        ).pack(
            side="left"
        )

        tk.Button(
            botoes,
            text="Restaurar padrao",
            bg=C["panel"],
            fg=C["dim"],
            bd=0,
            padx=10,
            pady=7,
            font=("Consolas", 8),
            cursor="hand2",
            activebackground=C["border"],
            command=self._restaurar
        ).pack(
            side="left",
            padx=8
        )


    def _restaurar(self):
        for var, texto in zip(
            self.vars,
            self.DEFAULTS
        ):
            var.set(texto)


    def _salvar(self):
        frases = []

        for i, var in enumerate(
            self.vars
        ):
            texto = var.get().strip()

            if not texto:
                texto = self.DEFAULTS[i]

            frases.append(texto)

        cfg["frases_waiting"] = frases

        save_cfg(cfg)

        self.comp.say(
            "Frases salvas!",
            "talking",
            2000
        )

        self.win.destroy()


#  JANELA: CONFIGURACOES

class SettingsWindow:

    WIDTH = 430
    HEIGHT = 680

    def __init__(self, parent, companion):
        self.comp = companion

        tema = cfg.get("tema", "escuro")

        self.colors = get_modern_palette(tema, "settings")

        self.win = ctk.CTkToplevel(parent)

        self.win.withdraw()
        self.win.overrideredirect(True)

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self.win.transient(parent)

        self._drag_x = 0
        self._drag_y = 0

        self._build()

        self.win.update_idletasks()

        _position_near_marvin(
            self.win,
            self.comp
        )

        self.win.deiconify()
        self.win.lift()
        self.win.grab_set()
        self.win.focus_force()

        self.win.bind(
            "<Escape>",
            lambda e: self.win.destroy()
        )

    # ==========================================================
    # JANELA
    # ==========================================================

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
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y

        self.win.geometry(
            f"+{x}+{y}"
        )

    # ==========================================================
    # COMPONENTES
    # ==========================================================

    def _section_title(
        self,
        parent,
        texto
    ):
        ctk.CTkLabel(
            parent,
            text=texto.upper(),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        ).pack(
            fill="x",
            pady=(18, 7)
        )

    def _toggle_row(
        self,
        parent,
        titulo,
        descricao,
        variable
    ):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=12,
            pady=10
        )

        text_area = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )

        text_area.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            text_area,
            text=titulo,
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            )
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            text_area,
            text=descricao,
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9
            )
        ).pack(
            fill="x",
            pady=(1, 0)
        )

        switch = ctk.CTkSwitch(
            row,
            text="",
            variable=variable,
            width=42,
            progress_color=self.colors["accent"],
            button_color=self.colors["card"],
            button_hover_color=self.colors["accent_hover"]
        )

        switch.pack(
            side="right",
            padx=(12, 0)
        )

    def _slider_block(
        self,
        parent,
        titulo,
        variable,
        from_,
        to,
        steps,
        valor,
        command
    ):
        block = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        block.pack(
            fill="x",
            pady=(0, 14)
        )

        top = ctk.CTkFrame(
            block,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            pady=(0, 7)
        )

        ctk.CTkLabel(
            top,
            text=titulo,
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            )
        ).pack(
            side="left"
        )

        badge = ctk.CTkLabel(
            top,
            text=valor,
            width=50,
            height=24,
            corner_radius=7,
            fg_color=self.colors["surface"],
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        )

        badge.pack(
            side="right"
        )

        slider = ctk.CTkSlider(
            block,
            variable=variable,
            from_=from_,
            to=to,
            number_of_steps=steps,
            fg_color=self.colors["border"],
            progress_color=self.colors["accent"],
            button_color=self.colors["card"],
            button_hover_color=self.colors["accent_hover"],
            height=18,
            command=lambda value: command(
                value,
                badge
            )
        )

        slider.pack(
            fill="x"
        )

        # CustomTkinter nao rola o CTkScrollableFrame quando
        # o cursor esta sobre um CTkSlider.
        # Redirecionamos esse evento para o scroll da pagina.
        slider.bind(
            "<MouseWheel>",
            self._scroll_settings_from_control,
            add="+"
        )

        return slider

    # ==========================================================
    # CALLBACKS VISUAIS
    # ==========================================================

    def _tema_visual_changed(self, valor):
        if valor == "Claro":
            self.v_tema.set("claro")
        else:
            self.v_tema.set("escuro")

    def _toggle_size_edit(self):
        """
        Os controles de tamanho so podem ser alterados
        quando 'Editar tamanho' estiver marcado.
        """

        enabled = bool(
            self.v_edit_size.get()
        )

        state = (
            "normal"
            if enabled
            else "disabled"
        )

        for slider in (
            getattr(
                self,
                "size_normal_slider",
                None
            ),
            getattr(
                self,
                "size_compact_slider",
                None
            ),
            getattr(
                self,
                "opacity_slider",
                None
            ),
        ):
            if slider is None:
                continue

            slider.configure(
                state=state,
                progress_color=(
                    self.colors["accent"]
                    if enabled
                    else self.colors["border"]
                ),
                button_color=(
                    self.colors["card"]
                    if enabled
                    else self.colors["surface"]
                ),
                button_hover_color=(
                    self.colors["accent_hover"]
                    if enabled
                    else self.colors["surface"]
                )
            )

        if (
            not enabled
            and hasattr(
                self,
                "size_preview_image_label"
            )
        ):
            self._clear_size_preview()


    def _clear_size_preview(self):
        """
        Limpa a demonstracao visual dos tamanhos.
        """

        if not hasattr(
            self,
            "size_preview_image_label"
        ):
            return

        self._size_preview_photo = None

        self.size_preview_image_label.configure(
            image=None,
            text=(
                "Mova um dos controles de tamanho "
                "para visualizar."
            )
        )

        self.size_preview_title.configure(
            text="Prévia — ajuste um tamanho"
        )


    def _update_size_preview(
        self,
        modo,
        valor
    ):
        """
        Mostra nas Configuracoes uma demonstracao do
        tamanho real do MARVIN sem trocar o modo atual.
        """

        if not bool(
            self.v_edit_size.get()
        ):
            return

        try:
            percentual = int(
                round(float(valor))
            )
        except (TypeError, ValueError):
            return

        percentual = max(
            60,
            min(120, percentual)
        )

        base = (
            Path(__file__)
            .resolve()
            .parent
            / "assets"
            / "marvin"
        )

        try:

            # ==================================================
            # MODO NORMAL
            # Mesma regra do MARVIN:
            # 150 px no tamanho 100%.
            # ==================================================

            if modo == "normal":

                arquivo = (
                    base
                    / "idle"
                    / "01.png"
                )

                if not arquivo.exists():
                    raise FileNotFoundError(
                        arquivo
                    )

                imagem = (
                    Image.open(arquivo)
                    .convert("RGBA")
                )

                tamanho = max(
                    1,
                    int(
                        150
                        * percentual
                        / 100
                    )
                )

                imagem = imagem.resize(
                    (
                        tamanho,
                        tamanho
                    ),
                    Image.Resampling.NEAREST
                )

                titulo = (
                    f"Prévia — Modo normal · "
                    f"{percentual}%"
                )


            # ==================================================
            # MODO COMPACTO
            # Repete a mesma regra usada pelo carregador real:
            # crop comum + limite de 92x64.
            # ==================================================

            elif modo == "compact":

                pasta = (
                    base
                    / "compact"
                )

                arquivos = [
                    pasta / "01.png",
                    pasta / "02.png",
                    pasta / "03.png",
                ]

                imagens = []

                for arquivo in arquivos:
                    if arquivo.exists():
                        imagens.append(
                            Image.open(
                                arquivo
                            ).convert("RGBA")
                        )

                if not imagens:
                    raise FileNotFoundError(
                        pasta
                    )

                caixas = []

                for img in imagens:
                    bbox = (
                        img
                        .getchannel("A")
                        .getbbox()
                    )

                    if bbox:
                        caixas.append(
                            bbox
                        )

                if not caixas:
                    return

                left = min(
                    b[0]
                    for b in caixas
                )

                top = min(
                    b[1]
                    for b in caixas
                )

                right = max(
                    b[2]
                    for b in caixas
                )

                bottom = max(
                    b[3]
                    for b in caixas
                )

                crop_box = (
                    left,
                    top,
                    right,
                    bottom
                )

                largura = (
                    right
                    - left
                )

                altura = (
                    bottom
                    - top
                )

                escala_config = (
                    percentual
                    / 100.0
                )

                max_w = max(
                    1,
                    int(
                        92
                        * escala_config
                    )
                )

                max_h = max(
                    1,
                    int(
                        64
                        * escala_config
                    )
                )

                escala = min(
                    max_w / largura,
                    max_h / altura
                )

                novo_w = max(
                    1,
                    int(
                        largura
                        * escala
                    )
                )

                novo_h = max(
                    1,
                    int(
                        altura
                        * escala
                    )
                )

                imagem = (
                    imagens[0]
                    .crop(crop_box)
                    .resize(
                        (
                            novo_w,
                            novo_h
                        ),
                        Image.Resampling.NEAREST
                    )
                )

                titulo = (
                    f"Prévia — Modo compacto · "
                    f"{percentual}%"
                )

            else:
                return


            # ==================================================
            # MOSTRA A IMAGEM
            # ==================================================

            self._size_preview_photo = (
                ImageTk.PhotoImage(
                    imagem,
                    master=self.win
                )
            )

            self.size_preview_image_label.configure(
                image=self._size_preview_photo,
                text=""
            )

            self.size_preview_title.configure(
                text=titulo
            )

        except Exception as exc:

            self._size_preview_photo = None

            self.size_preview_image_label.configure(
                image=None,
                text="Não foi possível carregar a prévia."
            )

            self.size_preview_title.configure(
                text="Prévia"
            )

            print(
                "[MARVIN] Erro na previa de tamanho: "
                f"{exc}"
            )


    def _size_normal_changed(
        self,
        value,
        badge
    ):
        # Segunda camada da trava:
        # impede alteracoes por scroll ou qualquer outro evento
        # enquanto "Editar tamanho" estiver desmarcado.
        if not bool(self.v_edit_size.get()):
            atual = int(
                cfg.get(
                    "tamanho_normal",
                    self.v_size_normal.get()
                )
            )

            self.v_size_normal.set(
                atual
            )

            badge.configure(
                text=str(atual)
            )

            return

        value = int(
            round(float(value) / 5) * 5
        )

        badge.configure(
            text=str(value)
        )

        self._preview_size(
            "tamanho_normal",
            value
        )

        self._update_size_preview(
            "normal",
            value
        )

    def _size_compact_changed(
        self,
        value,
        badge
    ):
        if not bool(self.v_edit_size.get()):
            atual = int(
                cfg.get(
                    "tamanho_compacto",
                    self.v_size_compact.get()
                )
            )

            self.v_size_compact.set(
                atual
            )

            badge.configure(
                text=str(atual)
            )

            return

        value = int(
            round(float(value) / 5) * 5
        )

        badge.configure(
            text=str(value)
        )

        self._preview_size(
            "tamanho_compacto",
            value
        )

        self._update_size_preview(
            "compact",
            value
        )

    def _opacity_changed(
        self,
        value,
        badge
    ):
        if not bool(self.v_edit_size.get()):
            atual = float(
                cfg.get(
                    "opacidade",
                    self.v_op.get()
                )
            )

            self.v_op.set(
                atual
            )

            badge.configure(
                text=f"{atual:.2f}"
            )

            return

        value = round(
            float(value),
            2
        )

        badge.configure(
            text=f"{value:.2f}"
        )

        self._preview_opacity(
            value
        )

    # ==========================================================
    # INTERFACE
    # ==========================================================

    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"]
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        shell.grid_columnconfigure(
            0,
            weight=1
        )

        shell.grid_rowconfigure(
            2,
            weight=1
        )

        # ------------------------------------------------------
        # TITLEBAR
        # ------------------------------------------------------

        titlebar = ctk.CTkFrame(
            shell,
            height=48,
            corner_radius=0,
            fg_color="transparent"
        )

        titlebar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(4, 0)
        )

        titlebar.pack_propagate(False)

        mark = ctk.CTkLabel(
            titlebar,
            text="",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
                weight="bold"
            )
        )

        mark.pack(
            side="left",
            padx=(5, 8)
        )

        titulo = ctk.CTkLabel(
            titlebar,
            text="MARVIN — CONFIGURAÇÕES",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            )
        )

        titulo.pack(
            side="left"
        )

        fechar = ctk.CTkButton(
            titlebar,
            text="×",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["surface"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20
            ),
            command=self.win.destroy
        )

        fechar.pack(
            side="right"
        )

        for widget in (
            titlebar,
            mark,
            titulo
        ):
            widget.bind(
                "<ButtonPress-1>",
                self._drag_start
            )

            widget.bind(
                "<B1-Motion>",
                self._drag_move
            )

        ctk.CTkFrame(
            shell,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).grid(
            row=1,
            column=0,
            sticky="ew"
        )

        # ------------------------------------------------------
        # CONTEUDO
        # ------------------------------------------------------

        body = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["dim"]
        )

        # Usado para redirecionar a roda do mouse dos sliders
        # para a rolagem vertical das Configuracoes.
        self._settings_scroll = body

        body.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(18, 8),
            pady=(14, 4)
        )

        ctk.CTkLabel(
            body,
            text="Configurações",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=21,
                weight="bold"
            )
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            body,
            text="Personalize a aparência e o comportamento do MARVIN.",
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        ).pack(
            fill="x",
            pady=(2, 2)
        )

        # ======================================================
        # APARENCIA
        # ======================================================

        self._section_title(
            body,
            "Aparência"
        )

        self.v_tema = tk.StringVar(
            value=cfg.get(
                "tema",
                "escuro"
            )
        )

        tema_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        tema_card.pack(
            fill="x"
        )

        self.theme_selector = ctk.CTkSegmentedButton(
            tema_card,
            values=[
                "Escuro",
                "Claro"
            ],
            height=36,
            fg_color=self.colors["surface"],
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["surface"],
            unselected_hover_color=self.colors["border"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=self._tema_visual_changed
        )

        self.theme_selector.pack(
            fill="x",
            padx=4,
            pady=4
        )

        if self.v_tema.get() == "claro":
            self.theme_selector.set(
                "Claro"
            )
        else:
            self.theme_selector.set(
                "Escuro"
            )

        # ======================================================
        # COMPORTAMENTO
        # ======================================================

        self._section_title(
            body,
            "Comportamento"
        )

        self.v_som = tk.BooleanVar(
            value=cfg.get(
                "som",
                True
            )
        )

        self.v_startup = tk.BooleanVar(
            value=_startup_enabled()
        )

        behavior_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        behavior_card.pack(
            fill="x"
        )

        self._toggle_row(
            behavior_card,
            "Som ao receber lembrete",
            "Toca um aviso quando uma tarefa chegar.",
            self.v_som
        )

        ctk.CTkFrame(
            behavior_card,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).pack(
            fill="x",
            padx=12
        )

        self._toggle_row(
            behavior_card,
            "Iniciar com o Windows",
            "Abre o MARVIN automaticamente ao entrar.",
            self.v_startup
        )

        # ======================================================
        # TAMANHO
        # ======================================================

        self._section_title(
            body,
            "Tamanho e exibição"
        )

        self.v_size_normal = tk.IntVar(
            value=cfg.get(
                "tamanho_normal",
                100
            )
        )

        self.v_size_compact = tk.IntVar(
            value=cfg.get(
                "tamanho_compacto",
                85
            )
        )

        self.v_op = tk.DoubleVar(
            value=cfg.get(
                "opacidade",
                1.0
            )
        )


        # ------------------------------------------------------
        # PROTECAO DOS CONTROLES DE TAMANHO
        # ------------------------------------------------------

        self.v_edit_size = tk.BooleanVar(
            value=False
        )

        self.edit_size_check = ctk.CTkCheckBox(
            body,
            text="Editar tamanho",
            variable=self.v_edit_size,
            onvalue=True,
            offvalue=False,
            command=self._toggle_size_edit,
            height=26,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            border_width=1,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            border_color=self.colors["border"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            )
        )

        self.edit_size_check.pack(
            fill="x",
            pady=(0, 12)
        )

        self.size_normal_slider = self._slider_block(
            body,
            "Tamanho do MARVIN",
            self.v_size_normal,
            60,
            120,
            12,
            str(self.v_size_normal.get()),
            self._size_normal_changed
        )

        self.size_compact_slider = self._slider_block(
            body,
            "Modo compacto",
            self.v_size_compact,
            60,
            120,
            12,
            str(self.v_size_compact.get()),
            self._size_compact_changed
        )

        # ------------------------------------------------------
        # PREVIA DE TAMANHO
        # ------------------------------------------------------

        self.size_preview_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        self.size_preview_card.pack(
            fill="x",
            pady=(12, 6)
        )

        self.size_preview_title = ctk.CTkLabel(
            self.size_preview_card,
            text="Prévia — ajuste um tamanho",
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        )

        self.size_preview_title.pack(
            fill="x",
            padx=14,
            pady=(10, 4)
        )

        self.size_preview_area = ctk.CTkFrame(
            self.size_preview_card,
            height=210,
            fg_color=self.colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )

        self.size_preview_area.pack(
            fill="x",
            padx=12,
            pady=(4, 12)
        )

        self.size_preview_area.pack_propagate(
            False
        )

        self.size_preview_image_label = ctk.CTkLabel(
            self.size_preview_area,
            text=(
                "Mova um dos controles de tamanho "
                "para visualizar."
            ),
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        )

        self.size_preview_image_label.pack(
            expand=True
        )

        self._size_preview_photo = None

        self.opacity_slider = self._slider_block(
            body,
            "Opacidade",
            self.v_op,
            0.3,
            1.0,
            14,
            f"{self.v_op.get():.2f}",
            self._opacity_changed
        )

        # Os tres controles ja existem neste ponto.
        # Aplicamos a trava somente agora.
        self._toggle_size_edit()

        # ======================================================
        # FRASES
        # ======================================================

        self._section_title(
            body,
            "Frases do MARVIN"
        )

        ctk.CTkLabel(
            body,
            text=(
                "Uma frase por linha. "
                "O MARVIN escolhe uma aleatoriamente."
            ),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        ).pack(
            fill="x",
            pady=(0, 6)
        )

        self.txt_frases = ctk.CTkTextbox(
            body,
            height=92,
            corner_radius=9,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            ),
            wrap="word"
        )

        self.txt_frases.pack(
            fill="x"
        )

        frases_atuais = cfg.get(
            "frases_idle",
            _IDLE_MSGS
        )

        if not isinstance(
            frases_atuais,
            list
        ):
            frases_atuais = _IDLE_MSGS

        self.txt_frases.insert(
            "1.0",
            "\n".join(
                frases_atuais
            )
        )

        ctk.CTkButton(
            body,
            text="Personalizar frases de espera",
            height=36,
            corner_radius=8,
            fg_color=self.colors["surface"],
            hover_color=self.colors["border"],
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=lambda: WaitingPhrasesWindow(
                self.win,
                self.comp
            )
        ).pack(
            fill="x",
            pady=(8, 0)
        )

        # ======================================================
        # DADOS
        # ======================================================

        self._section_title(
            body,
            "Dados"
        )

        ctk.CTkButton(
            body,
            text="Limpar tarefas concluídas há mais de 30 dias",
            height=38,
            corner_radius=8,
            fg_color=self.colors["danger_bg"],
            hover_color=self.colors["border"],
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["danger_fg"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=self._limpar
        ).pack(
            fill="x"
        )

        db_box = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )

        db_box.pack(
            fill="x",
            pady=(8, 18)
        )

        ctk.CTkLabel(
            db_box,
            text=f"DB: {DB_F}",
            text_color=self.colors["dim"],
            anchor="w",
            justify="left",
            wraplength=350,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9
            )
        ).pack(
            fill="x",
            padx=10,
            pady=8
        )

        # ======================================================
        # FOOTER
        # ======================================================

        footer = ctk.CTkFrame(
            shell,
            fg_color=self.colors["card"],
            corner_radius=0
        )

        footer.grid(
            row=3,
            column=0,
            sticky="ew"
        )

        ctk.CTkFrame(
            footer,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).pack(
            fill="x"
        )

        ctk.CTkButton(
            footer,
            text="Salvar alterações",
            height=42,
            corner_radius=9,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            command=self._salvar
        ).pack(
            fill="x",
            padx=18,
            pady=12
        )

    # ==========================================================
    # SCROLL
    # ==========================================================

    def _scroll_settings_from_control(
        self,
        event
    ):
        """
        Faz a roda do mouse sobre os sliders se comportar
        exatamente como a rolagem normal das Configuracoes.
        """

        try:
            canvas = getattr(
                self._settings_scroll,
                "_parent_canvas",
                None
            )

            if canvas is None:
                return "break"

            delta = getattr(
                event,
                "delta",
                0
            )

            if not delta:
                return "break"

            # Mesma formula usada internamente pelo
            # CTkScrollableFrame no Windows.
            unidades = -int(
                delta / 6
            )

            if unidades:
                canvas.yview(
                    "scroll",
                    unidades,
                    "units"
                )

        except Exception:
            pass

        return "break"

    # ==========================================================
    # PREVIEWS
    # ==========================================================

    def _preview_size(self, chave, valor):
        try:
            valor = int(float(valor))
        except (TypeError, ValueError):
            return

        cfg[chave] = valor
        save_cfg(cfg)

        try:
            self.comp._reload_sprites()
        except Exception as exc:
            print(
                f"[MARVIN] Erro ao atualizar tamanho: {exc}"
            )

    def _preview_opacity(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return

        valor = max(
            0.3,
            min(1.0, valor)
        )

        cfg["opacidade"] = round(
            valor,
            2
        )

        save_cfg(cfg)

        try:
            self.comp.root.attributes(
                "-alpha",
                valor
            )
        except Exception as exc:
            print(
                f"[MARVIN] Erro ao alterar opacidade: {exc}"
            )

    # ==========================================================
    # SALVAR
    # ==========================================================

    def _salvar(self):
        tema_anterior = cfg.get(
            "tema",
            "escuro"
        )

        cfg["tema"] = self.v_tema.get()

        cfg["som"] = self.v_som.get()

        cfg["opacidade"] = round(
            self.v_op.get(),
            2
        )

        cfg["tamanho_normal"] = int(
            self.v_size_normal.get()
        )

        cfg["tamanho_compacto"] = int(
            self.v_size_compact.get()
        )

        frases = [
            linha.strip()
            for linha in self.txt_frases.get(
                "1.0",
                "end"
            ).splitlines()
            if linha.strip()
        ]

        cfg["frases_idle"] = (
            frases
            if frases
            else list(_IDLE_MSGS)
        )

        save_cfg(cfg)

        tema_mudou = (
            tema_anterior
            != cfg["tema"]
        )

        startup_ok = _set_startup_enabled(
            self.v_startup.get()
        )

        if not startup_ok:
            messagebox.showwarning(
                "MARVIN",
                "Nao foi possivel alterar a inicializacao com o Windows."
            )

        self.comp._reload_sprites()

        try:
            self.comp.root.attributes(
                "-alpha",
                cfg["opacidade"]
            )
        except Exception:
            pass

        if tema_mudou:
            self.win.destroy()

            # Para explicitamente o icone antigo da bandeja
            # antes de substituir o processo.
            tray_icon = getattr(
                self.comp,
                "_tray_icon",
                None
            )

            if tray_icon is not None:
                try:
                    tray_icon.stop()
                except Exception:
                    pass
                finally:
                    self.comp._tray_icon = None

            os.execl(
                sys.executable,
                sys.executable,
                "-m",
                "marvin.main",
            )

            return

        self.comp.say(
            "Configuracoes salvas!",
            "talking",
            2500
        )

        self.win.destroy()

    def _limpar(self):
        db_limpar_antigas(30)

        self.comp.say(
            "Limpeza concluida!",
            "talking",
            2500
        )

        self.win.destroy()


class InteractionPanel:

    WIDTH = 232

    def __init__(
        self,
        root,
        companion,
        mode="idle",
    ):
        self.comp = companion
        self.root = root
        self.mode = mode

        self.tema = cfg.get(
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

    def _header(self, parent):

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


        # Cabeca do MARVIN
        icon_path = (
            Path(__file__)
            .resolve()
            .parent
            .parent
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
            # Fallback caso a imagem nao seja encontrada.
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
            parent
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


        body = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        body.pack(
            fill="x",
            padx=8,
            pady=(14, 7),
        )


        # ----------------------------------------------------
        # ICONE CENTRAL
        # ----------------------------------------------------

        if n == 0:
            icon_bg = self.colors[
                "green_bg"
            ]

            icon_fg = self.colors[
                "green"
            ]

            icon_text = "✓"

        else:
            icon_bg = self.colors[
                "orange_bg"
            ]

            icon_fg = self.colors[
                "accent"
            ]

            icon_text = str(
                min(n, 99)
            )


        icon = ctk.CTkFrame(
            body,

            width=34,
            height=34,

            corner_radius=17,

            fg_color=icon_bg,

            border_width=1,
            border_color=icon_fg,
        )

        icon.pack()

        icon.pack_propagate(
            False
        )


        ctk.CTkLabel(
            icon,

            text=icon_text,

            text_color=icon_fg,

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


        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

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

        ).pack(
            pady=(9, 0),
        )


        if n_hoje:
            hoje_texto = (
                "1 para hoje."
                if n_hoje == 1
                else
                f"{n_hoje} para hoje."
            )

            ctk.CTkLabel(
                body,

                text=hoje_texto,

                text_color=self.colors[
                    "dim"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                ),

            ).pack(
                pady=(2, 0),
            )


        if streak:
            streak_texto = (
                "1 concluída hoje"
                if streak == 1
                else
                f"{streak} concluídas hoje"
            )

            ctk.CTkLabel(
                body,

                text=streak_texto,

                text_color=self.colors[
                    "green"
                ],

                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                ),

            ).pack(
                pady=(2, 0),
            )


        # ----------------------------------------------------
        # ACOES
        # ----------------------------------------------------

        self._button(
            parent,

            "Central do MARVIN",

            lambda: [
                self._close(),
                self.comp._open_home()
            ],
        )


        if n:
            self._button(
                parent,

                "Ver tarefas",

                lambda: [
                    self._close(),
                    TaskWindow(
                        self.root,
                        self.comp
                    )
                ],
            )


        self._button(
            parent,

            "+ Nova tarefa",

            lambda: [
                self._close(),
                NewTaskWindow(
                    self.root,
                    self.comp
                )
            ],

            accent=True,
        )


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
            pady=(2, 11),
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


        queue = (
            self.comp
            ._reminder_queue
        )

        task = (
            queue[0]
            if queue
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
            queue
        )


        if n_fila > 1:
            ctk.CTkLabel(
                body,

                text=(
                    f"+{n_fila - 1} "
                    "lembrete(s) na fila"
                ),

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
                SnoozeWindow(
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
                TaskWindow(
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


class SnoozeWindow:

    WIDTH = 270
    HEIGHT = 330

    OPTS = [
        ("5 minutos", 5),
        ("15 minutos", 15),
        ("30 minutos", 30),
        ("1 hora", 60),
    ]

    def __init__(
        self,
        root,
        companion,
        task,
    ):
        self.root = root
        self.comp = companion
        self.task = task

        self.tema = cfg.get(
            "tema",
            "escuro"
        )

        self.colors = get_modern_palette(
            self.tema,
            "interaction"
        )

        ctk.set_appearance_mode(
            "Light"
            if self.tema == "claro"
            else "Dark"
        )

        self.win = ctk.CTkToplevel(
            root
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False
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

        self._build()

        _position_near_marvin(
            self.win,
            self.comp
        )

        self.win.bind(
            "<Escape>",
            lambda e: self._close()
        )

        self.win.bind(
            "<FocusOut>",
            self._on_focus_out
        )

        self.win.focus_force()


    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2,
        )

        # ====================================================
        # TOPO
        # ====================================================

        header = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
            padx=16,
            pady=(14, 4),
        )

        icon = ctk.CTkFrame(
            header,
            width=34,
            height=34,
            corner_radius=17,
            fg_color=self.colors["orange_bg"],
            border_width=1,
            border_color=self.colors["accent"],
        )

        icon.pack(
            side="left"
        )

        icon.pack_propagate(
            False
        )

        ctk.CTkLabel(
            icon,
            text="↻",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        title_wrap = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        title_wrap.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 0),
        )

        ctk.CTkLabel(
            title_wrap,
            text="Adiar tarefa",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            title_wrap,
            text="Escolha quando quer ser lembrado novamente",
            anchor="w",
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),
        ).pack(
            fill="x"
        )

        ctk.CTkButton(
            header,
            text="×",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["hover"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=18,
            ),
            command=self._close,
        ).pack(
            side="right",
            padx=(6, 0),
        )

        # ====================================================
        # TAREFA
        # ====================================================

        if self.task:
            task_card = ctk.CTkFrame(
                shell,
                fg_color=self.colors["bg"],
                corner_radius=9,
                border_width=1,
                border_color=self.colors["border"],
            )

            task_card.pack(
                fill="x",
                padx=16,
                pady=(8, 12),
            )

            ctk.CTkLabel(
                task_card,
                text=self.task[1],
                anchor="w",
                justify="left",
                wraplength=195,
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
            ).pack(
                fill="x",
                padx=11,
                pady=(8, 1),
            )

            ctk.CTkLabel(
                task_card,
                text=f"Horário original · {self.task[4][:5]}",
                anchor="w",
                text_color=self.colors["dim"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),
            ).pack(
                fill="x",
                padx=11,
                pady=(0, 8),
            )

        # ====================================================
        # OPCOES
        # ====================================================

        options = ctk.CTkFrame(
            shell,
            fg_color="transparent",
        )

        options.pack(
            fill="x",
            padx=16,
        )

        options.grid_columnconfigure(
            0,
            weight=1,
            uniform="snooze"
        )

        options.grid_columnconfigure(
            1,
            weight=1,
            uniform="snooze"
        )

        for i, (label, minutos) in enumerate(self.OPTS):

            row = i // 2
            column = i % 2

            button = ctk.CTkButton(
                options,
                text=label,
                height=42,
                corner_radius=9,
                fg_color="transparent",
                hover_color=self.colors["orange_bg"],
                border_width=1,
                border_color=self.colors["border"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
                command=lambda m=minutos:
                    self._snooze(m),
            )

            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(
                    (0, 4)
                    if column == 0
                    else (4, 0)
                ),
                pady=4,
            )

        ctk.CTkButton(
            shell,
            text="Cancelar",
            height=30,
            corner_radius=7,
            fg_color="transparent",
            hover_color=self.colors["hover"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
            command=self._close,
        ).pack(
            fill="x",
            padx=16,
            pady=(8, 13),
        )


    def _on_focus_out(
        self,
        event=None
    ):
        # Pequeno atraso para permitir que o clique
        # nos botoes seja processado antes de fechar.
        try:
            self.win.after(
                100,
                self._close_if_focus_lost
            )
        except Exception:
            pass


    def _close_if_focus_lost(self):

        try:
            focus = self.win.focus_get()

            if focus is None:
                self._close()

        except Exception:
            self._close()


    def _close(self):

        try:
            self.win.destroy()

        except Exception:
            pass


    def _snooze(
        self,
        minutes
    ):

        new_dt = (
            datetime.datetime.now()
            + datetime.timedelta(
                minutes=minutes
            )
        )

        if self.task:
            db_adiar(
                self.task[0],
                new_dt.strftime(
                    "%Y-%m-%d"
                ),
                new_dt.strftime(
                    "%H:%M"
                )
            )

        self.comp._next_reminder()

        self.comp.say(
            (
                "Adiado para "
                f"{new_dt.strftime('%H:%M')}."
            ),
            "talking",
            3000
        )

        self._close()


#  POPUP DE NOTIFICACAO (canto inferior direito)

#  POPUP DE NOTIFICACAO (canto inferior direito)

class NotifPopup:
    def __init__(self, root, companion, task, duration=0):
        self.root = root
        self.comp = companion
        self.task = task
        self.duration = duration

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=C["border"])

        inner = tk.Frame(self.win, bg=C["panel"])
        inner.pack(padx=1, pady=1)

        # Cabecalho
        hf = tk.Frame(inner, bg=C["panel"])
        hf.pack(fill="x", padx=8, pady=(8, 2))

        tk.Label(
            hf,
            text="Lembrete",
            bg=C["panel"],
            fg=C["orange"],
            font=("Consolas", 9, "bold")
        ).pack(side="left")

        tk.Button(
            hf,
            text="x",
            bg=C["panel"],
            fg=C["dim"],
            bd=0,
            font=("Consolas", 8),
            cursor="hand2",
            activebackground=C["panel"],
            activeforeground=C["red"],
            command=self._close
        ).pack(side="right")

        # Nome da tarefa
        tk.Label(
            inner,
            text=task[1],
            bg=C["panel"],
            fg=C["text"],
            font=("Consolas", 10, "bold"),
            wraplength=240,
            justify="left"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        # Descricao
        if task[2]:
            tk.Label(
                inner,
                text=task[2],
                bg=C["panel"],
                fg=C["dim"],
                font=("Consolas", 8),
                wraplength=240,
                justify="left"
            ).pack(anchor="w", padx=10, pady=(0, 8))

        # Horario
        tk.Label(
            inner,
            text=f"Horario: {task[4][:5]}",
            bg=C["panel"],
            fg=C["dim"],
            font=("Consolas", 7)
        ).pack(anchor="w", padx=10, pady=(0, 6))

        tk.Frame(
            inner,
            bg=C["border"],
            height=1
        ).pack(fill="x", padx=8, pady=3)

        # Botoes
        bf = tk.Frame(inner, bg=C["panel"])
        bf.pack(fill="x", padx=6, pady=6)

        tk.Button(
            bf,
            text="Concluir",
            bg=C["green"],
            fg=C["win_bg"],
            bd=0,
            padx=10,
            pady=6,
            font=("Consolas", 8, "bold"),
            cursor="hand2",
            activebackground=C["accent"],
            activeforeground=C["win_bg"],
            command=self._complete
        ).pack(side="left", padx=2)

        tk.Button(
            bf,
            text="Adiar",
            bg=C["orange"],
            fg=C["win_bg"],
            bd=0,
            padx=10,
            pady=6,
            font=("Consolas", 8, "bold"),
            cursor="hand2",
            activebackground=C["accent"],
            activeforeground=C["win_bg"],
            command=self._snooze
        ).pack(side="left", padx=2)

        tk.Button(
            bf,
            text="Tarefas",
            bg=C["win_bg"],
            fg=C["accent"],
            bd=0,
            padx=10,
            pady=6,
            font=("Consolas", 8),
            cursor="hand2",
            activebackground=C["border"],
            activeforeground=C["text"],
            command=self._tasks
        ).pack(side="left", padx=2)

        self.win.update_idletasks()

        # Posiciona no canto inferior direito
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        ww = self.win.winfo_width()
        wh = self.win.winfo_height()

        self.win.geometry(
            f"+{sw - ww - 16}+{sh - wh - 56}"
        )

        # Se duration > 0, fecha automaticamente.
        # Para lembretes usamos 0, portanto fica aberto.
        if self.duration > 0:
            self.win.after(self.duration, self._close)

    def _close(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def _complete(self):
        # Garante que a tarefa ainda e a primeira da fila
        if self.comp._reminder_queue:
            if self.comp._reminder_queue[0][0] == self.task[0]:
                self.comp.complete_task()
            else:
                db_concluir(self.task[0])

        self._close()

    def _snooze(self):
        self._close()

        SnoozeWindow(
            self.root,
            self.comp,
            self.task
        )

    def _tasks(self):
        self._close()

        TaskWindow(
            self.root,
            self.comp
        )


#  PERSONAGEM PRINCIPAL — MARVIN


class MarvinCompanion:

    # ========================================================
    # TIMINGS
    # ========================================================

    REMINDER_POLL_SECONDS = 1.0
    RECURRENT_REMINDER_RESET_MS = 95_000

    BLINK_MIN_SECONDS = 3.0
    BLINK_MAX_SECONDS = 6.0

    YAWN_MIN_SECONDS = 45.0
    YAWN_MAX_SECONDS = 90.0

    ALERT_FRAME_SECONDS = 0.18
    COMPACT_FRAME_SECONDS = 0.35

    ANIMATION_TICK_MS = 50
    W, H = 180, 260

    COMPACT_W = 100
    COMPACT_H = 80

    # Tempo total desde que o lembrete apareceu.
    # 1min -> imagem 01
    # 1min30 -> imagem 02
    # 2min -> imagem 03
    WAITING_TIMES = (30.0, 32.0, 60.0)

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
        saved_x = cfg.get("pos_x")
        saved_y = cfg.get("pos_y")

        sx = (
            saved_x
            if isinstance(saved_x, int)
            else sw - self.W - 20
        )

        sy = (
            saved_y
            if isinstance(saved_y, int)
            else sh - self.H - 60
        )

        self.root.geometry(f"{self.W}x{self.H}+{sx}+{sy}")

        self.cv = tk.Canvas(self.root, width=self.W, height=self.H,
                             bg=TK, highlightthickness=0)
        self.cv.pack()

        # Sprites do MARVIN
        self._idle_frames = self._load_idle_frames()
        self._alert_frames = self._load_alert_frames()
        self._waiting_frames = self._load_waiting_frames()
        self._happy_frame = self._load_happy_frame()
        self._compact_frames = self._load_compact_frames()
        self._yawn_frames = self._load_yawn_frames()

        # Controle da piscada
        self._next_blink = time.monotonic() + random.uniform(self.BLINK_MIN_SECONDS, self.BLINK_MAX_SECONDS)
        self._blink_until = 0.0

        # Controle do bocejo
        self._next_yawn = time.monotonic() + random.uniform(self.YAWN_MIN_SECONDS, self.YAWN_MAX_SECONDS)
        self._yawn_index = 0
        self._yawn_last_frame = 0.0
        self._yawn_sequence = [0, 1, 1, 1, 0]

        # Controle da animacao de alerta
        self._alert_frame_index = 0
        self._alert_last_frame = time.monotonic()

        # Momento em que o lembrete atual apareceu.
        self._reminder_started_at = None

        # Estagio da reacao ao ignorar o lembrete.
        # 0 = normal
        # 1 = waiting 01
        # 2 = waiting 02
        # 3 = waiting 03
        self._waiting_reaction_stage = 0

        # Controle do modo compacto / Nao Perturbe
        self._compact_mode = False
        self._compact_enabled = False
        self._compact_frame_index = 0
        self._compact_last_frame = time.monotonic()
        self._compact_sequence = [0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0]
        self._normal_pos = None

        # Controle exclusivo do modo compacto.
        self._compact_drag_active = False
        self._compact_drag_offset_x = 0
        self._compact_drag_start = None
        self._compact_has_position = False

        # Estado
        self.t               = 0.0
        self.state           = "thinking"
        self.bubble          = ""
        self.b_timer         = 0

        # Controle de encerramento da thread de lembretes.
        self._reminder_stop = threading.Event()
        self._reminder_thread = None
        self._bubble_deadline = None
        self._reminder_queue = []
        self._panel_open     = False
        self._dragging       = False

        # Interação do balão de lembrete
        self._bubble_mode = "normal"
        self._bubble_hover = None
        self._drag_dist      = 0
        self._dx = self._dy  = 0

        # Bandeja do Windows
        self._tray_icon = None
        self._tray_actions = queue.Queue()
        self._is_hidden = False

        # Processa comandos vindos do icone da bandeja
        # sempre pela thread principal do Tkinter.
        self.root.after(
            100,
            self._process_tray_actions
        )
        
        

        # Frases idle
        self._idle_interval  = 45000
        self._schedule_idle()

        # Eventos
        self.cv.bind("<ButtonPress-1>",   self._drag_start)
        self.cv.bind("<B1-Motion>",       self._drag_move)
        self.cv.bind("<ButtonRelease-1>", self._drag_end)
        self.cv.bind("<Button-3>",        self._show_menu)

        self.root.protocol("WM_DELETE_WINDOW", self._hide_marvin)
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
            label="Central do MARVIN",
            command=self._open_home)                                 # indice 0

        self.ctx.add_command(
            label="+ Nova Tarefa  [Ctrl+Shift+N]",
            command=lambda: NewTaskWindow(self.root, self))          # indice 1

        self.ctx.add_separator()                                     # indice 2

        self.ctx.add_command(
            label=self._np_label(),
            command=self._toggle_np)                                 # indice 3

        self.ctx.add_command(
            label="Configuracoes",
            command=lambda: SettingsWindow(self.root, self))         # indice 4

        self.ctx.add_separator()                                     # indice 5

        self.ctx.add_command(
            label="Ocultar MARVIN",
            command=self._hide_marvin)                               # indice 6

        self.ctx.add_separator()                                     # indice 7

        self.ctx.add_command(
            label="Sair",
            command=self._on_close)                                  # indice 8

        self._start_tray()

        self._animate()
        self._start_reminders()

        # Carrega extensoes opcionais instaladas.
        self._extensions = carregar_extensoes(self)

        threading.Thread(target=db_limpar_antigas, daemon=True).start()
        self.root.after(900, self._inicio_do_dia)

    # ── Bandeja do Windows ─────────────────────────────────────────────────

    def _tray_dispatch(self, callback):
        """
        O pystray roda em outra thread.
        Apenas coloca a acao na fila; o Tkinter
        executa depois na thread principal.
        """
        self._tray_actions.put(callback)


    def _process_tray_actions(self):
        try:
            while True:
                callback = self._tray_actions.get_nowait()

                try:
                    callback()
                except Exception as exc:
                    print(
                        f"[MARVIN] Erro em acao da bandeja: {exc}"
                    )

        except queue.Empty:
            pass

        try:
            self.root.after(
                100,
                self._process_tray_actions
            )
        except tk.TclError:
            pass


    def _tray_image(self):
        """
        Usa um sprite existente do MARVIN
        como icone da bandeja.
        """
        base = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
        )

        arquivos = [
            base / "compact" / "01.png",
            base / "idle" / "01.png",
        ]

        for arquivo in arquivos:
            if not arquivo.exists():
                continue

            try:
                imagem = Image.open(
                    arquivo
                ).convert("RGBA")

                bbox = imagem.getchannel("A").getbbox()

                if bbox:
                    imagem = imagem.crop(bbox)

                imagem.thumbnail(
                    (56, 56),
                    Image.Resampling.NEAREST
                )

                canvas = Image.new(
                    "RGBA",
                    (64, 64),
                    (0, 0, 0, 0)
                )

                x = (
                    64 - imagem.width
                ) // 2

                y = (
                    64 - imagem.height
                ) // 2

                canvas.paste(
                    imagem,
                    (x, y),
                    imagem
                )

                return canvas

            except Exception as exc:
                print(
                    f"[MARVIN] Erro ao carregar icone: {exc}"
                )

        return None


    def _start_tray(self):
        if pystray is None:
            print(
                "[MARVIN] pystray nao instalado. "
                "Bandeja desativada."
            )
            return

        if sys.platform != "win32":
            return

        imagem = self._tray_image()

        if imagem is None:
            print(
                "[MARVIN] Nao foi possivel criar "
                "o icone da bandeja."
            )
            return

        menu = pystray.Menu(

            pystray.MenuItem(
                "Mostrar MARVIN",
                lambda icon, item:
                    self._tray_dispatch(
                        self._show_marvin
                    ),
                default=True
            ),

            pystray.MenuItem(
                "Nova tarefa",
                lambda icon, item:
                    self._tray_dispatch(
                        self._tray_new_task
                    )
            ),

            pystray.MenuItem(
                "Central do MARVIN",
                lambda icon, item:
                    self._tray_dispatch(
                        self._open_home
                    )
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Modo compacto",
                lambda icon, item:
                    self._tray_dispatch(
                        self._toggle_np
                    ),
                checked=lambda item:
                    self._compact_enabled
            ),

            pystray.MenuItem(
                "Configuracoes",
                lambda icon, item:
                    self._tray_dispatch(
                        self._tray_settings
                    )
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Sair",
                lambda icon, item:
                    self._tray_dispatch(
                        self._on_close
                    )
            ),
        )

        self._tray_icon = pystray.Icon(
            "MARVIN",
            imagem,
            "MARVIN",
            menu
        )

        self._tray_icon.run_detached()

        print(
            "[MARVIN] Icone da bandeja iniciado."
        )


    def _show_marvin(self):
        try:
            self.root.deiconify()
            self.root.lift()

            self.root.attributes(
                "-topmost",
                True
            )

            self._is_hidden = False

        except tk.TclError:
            pass


    def _hide_marvin(self):
        """
        Esconde o personagem, mas mantem
        lembretes e bandeja funcionando.
        """
        try:
            if self._compact_mode:
                self._save_compact_position()
            else:
                cfg["pos_x"] = self.root.winfo_x()
                cfg["pos_y"] = self.root.winfo_y()
                save_cfg(cfg)

            self.root.withdraw()
            self._is_hidden = True

        except tk.TclError:
            pass


    def _open_home(self):
        self._show_marvin()

        abrir_home(
            self.root,
            self,
            abrir_tarefas=lambda:
                TaskWindow(self.root, self),
            nova_tarefa=lambda:
                NewTaskWindow(self.root, self),
            abrir_checklist=lambda:
                abrir_checklist(self.root),
            abrir_resumo=self._resumo_do_dia,
            abrir_config=lambda:
                SettingsWindow(self.root, self),
        )


    def _tray_new_task(self):
        self._show_marvin()

        NewTaskWindow(
            self.root,
            self
        )


    def _tray_tasks(self):
        self._show_marvin()

        TaskWindow(
            self.root,
            self
        )


    def _tray_checklist(self):
        self._show_marvin()

        abrir_checklist(
            self.root
        )


    def _tray_summary(self):
        self._show_marvin()
        self._resumo_do_dia()


    def _tray_settings(self):
        self._show_marvin()

        SettingsWindow(
            self.root,
            self
        )


    # ── Modo compacto nativo do Windows ─────────────────────────────────────

    def _win32_root_hwnd(self):
        """
        Retorna o HWND real da janela principal.
        O winfo_id() pode apontar para uma janela filha
        interna do Tkinter.
        """
        if sys.platform != "win32":
            return None

        try:

            user32 = ctypes.windll.user32

            user32.GetAncestor.argtypes = [
                wintypes.HWND,
                wintypes.UINT,
            ]
            user32.GetAncestor.restype = wintypes.HWND

            hwnd = self.root.winfo_id()

            GA_ROOT = 2

            root_hwnd = user32.GetAncestor(
                hwnd,
                GA_ROOT
            )

            return root_hwnd or hwnd

        except Exception as exc:
            print(
                f"[MARVIN] Erro ao obter HWND: {exc}"
            )
            return None


    def _win32_cursor_pos(self):
        if sys.platform == "win32":
            try:

                point = wintypes.POINT()

                if ctypes.windll.user32.GetCursorPos(
                    ctypes.byref(point)
                ):
                    return (
                        point.x,
                        point.y
                    )

            except Exception:
                pass

        return (
            self.root.winfo_pointerx(),
            self.root.winfo_pointery()
        )


    def _win32_workarea_from_point(self, x, y):
        """
        Retorna:
        left, top, right, bottom

        usando as coordenadas do desktop virtual.
        """
        if sys.platform == "win32":
            try:


                user32 = ctypes.windll.user32

                user32.MonitorFromPoint.argtypes = [
                    wintypes.POINT,
                    wintypes.DWORD,
                ]
                user32.MonitorFromPoint.restype = (
                    ctypes.c_void_p
                )

                user32.GetMonitorInfoW.argtypes = [
                    ctypes.c_void_p,
                    ctypes.POINTER(MONITORINFO),
                ]
                user32.GetMonitorInfoW.restype = (
                    wintypes.BOOL
                )

                point = wintypes.POINT(
                    int(x),
                    int(y)
                )

                monitor = user32.MonitorFromPoint(
                    point,
                    2
                )

                info = MONITORINFO()
                info.cbSize = ctypes.sizeof(
                    MONITORINFO
                )

                if (
                    monitor
                    and user32.GetMonitorInfoW(
                        monitor,
                        ctypes.byref(info)
                    )
                ):
                    return (
                        info.rcWork.left,
                        info.rcWork.top,
                        info.rcWork.right,
                        info.rcWork.bottom,
                    )

            except Exception as exc:
                print(
                    f"[MARVIN] Erro ao detectar monitor: {exc}"
                )

        return (
            0,
            0,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight()
        )


    def _win32_window_rect(self):
        hwnd = self._win32_root_hwnd()

        if hwnd is not None:
            try:

                rect = wintypes.RECT()

                if ctypes.windll.user32.GetWindowRect(
                    hwnd,
                    ctypes.byref(rect)
                ):
                    return (
                        rect.left,
                        rect.top,
                        rect.right,
                        rect.bottom,
                    )

            except Exception:
                pass

        x = self.root.winfo_x()
        y = self.root.winfo_y()

        return (
            x,
            y,
            x + self.root.winfo_width(),
            y + self.root.winfo_height()
        )


    def _win32_move_resize(self, x, y, width, height):
        """
        Move a janela usando coordenadas absolutas reais,
        inclusive X negativo em monitores à esquerda.
        """
        hwnd = self._win32_root_hwnd()

        if (
            sys.platform == "win32"
            and hwnd is not None
        ):
            try:

                user32 = ctypes.windll.user32

                user32.SetWindowPos.argtypes = [
                    wintypes.HWND,
                    wintypes.HWND,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    wintypes.UINT,
                ]

                user32.SetWindowPos.restype = (
                    wintypes.BOOL
                )

                SWP_NOZORDER = 0x0004
                SWP_NOACTIVATE = 0x0010
                SWP_SHOWWINDOW = 0x0040

                ok = user32.SetWindowPos(
                    hwnd,
                    None,
                    int(x),
                    int(y),
                    int(width),
                    int(height),
                    SWP_NOZORDER
                    | SWP_NOACTIVATE
                    | SWP_SHOWWINDOW
                )

                if ok:
                    return True

            except Exception as exc:
                print(
                    f"[MARVIN] Erro ao mover janela: {exc}"
                )

        return False


    def _save_compact_position(self):
        left, top, right, bottom = (
            self._win32_window_rect()
        )

        cfg["pos_compact_x"] = int(left)
        cfg["pos_compact_y"] = int(top)

        self._compact_has_position = True

        save_cfg(cfg)


    def _enter_compact_layout(
        self,
        remember_normal=False
    ):
        if remember_normal:
            rect = self._win32_window_rect()

            self._normal_pos = (
                rect[0],
                rect[1]
            )

            cfg["pos_x"] = rect[0]
            cfg["pos_y"] = rect[1]

        # Na primeira ativacao desta execucao,
        # ignora posicoes antigas possivelmente
        # deixadas pelos testes anteriores.
        if self._compact_has_position:
            compact_x = cfg.get(
                "pos_compact_x"
            )
            compact_y = cfg.get(
                "pos_compact_y"
            )
        else:
            rect = self._win32_window_rect()

            compact_x = rect[0]
            compact_y = rect[1]

        if not isinstance(compact_x, int):
            compact_x = self.root.winfo_x()

        if not isinstance(compact_y, int):
            compact_y = self.root.winfo_y()

        left, top, right, bottom = (
            self._win32_workarea_from_point(
                compact_x + self.COMPACT_W // 2,
                compact_y
            )
        )

        compact_x = max(
            left,
            min(
                compact_x,
                right - self.COMPACT_W
            )
        )

        compact_y = (
            bottom - self.COMPACT_H
        )

        self._compact_mode = True

        self.cv.config(
            width=self.COMPACT_W,
            height=self.COMPACT_H
        )

        self._win32_move_resize(
            compact_x,
            compact_y,
            self.COMPACT_W,
            self.COMPACT_H
        )

        cfg["pos_compact_x"] = compact_x
        cfg["pos_compact_y"] = compact_y

        self._compact_has_position = True

        save_cfg(cfg)


    def _restore_normal_layout(self):
        self._compact_drag_active = False
        self._compact_mode = False

        self.cv.config(
            width=self.W,
            height=self.H
        )

        pos = self._normal_pos

        if pos is None:
            px = cfg.get("pos_x")
            py = cfg.get("pos_y")

            if (
                isinstance(px, int)
                and isinstance(py, int)
            ):
                pos = (px, py)

        if pos is None:
            pos = (
                self.root.winfo_x(),
                self.root.winfo_y()
            )

        self._win32_move_resize(
            pos[0],
            pos[1],
            self.W,
            self.H
        )


    def _expand_compact_for_reminder(self):
        """
        Expande o MARVIN no mesmo monitor em que
        a cabeça compacta está.
        """
        rect = self._win32_window_rect()

        compact_x = rect[0]
        compact_y = rect[1]

        cfg["pos_compact_x"] = compact_x
        cfg["pos_compact_y"] = compact_y

        self._compact_has_position = True
        self._compact_drag_active = False
        self._compact_mode = False

        left, top, right, bottom = (
            self._win32_workarea_from_point(
                compact_x + self.COMPACT_W // 2,
                compact_y + self.COMPACT_H // 2
            )
        )

        x = max(
            left,
            min(
                compact_x,
                right - self.W
            )
        )

        y = max(
            top,
            bottom - self.H
        )

        self.cv.config(
            width=self.W,
            height=self.H
        )

        self._win32_move_resize(
            x,
            y,
            self.W,
            self.H
        )

        save_cfg(cfg)


    def _finish_compact_drag(self):
        if not self._compact_drag_active:
            return

        self._compact_drag_active = False
        self._save_compact_position()


    def _compact_drag_tick(self):
        """
        Arraste global: continua funcionando mesmo quando
        o mouse sai da janela e atravessa para outro monitor.
        """
        if (
            not self._compact_drag_active
            or not self._compact_mode
        ):
            return

        if sys.platform == "win32":
            try:

                # Se o botao esquerdo foi solto,
                # encerra mesmo que o Tkinter nao receba
                # ButtonRelease na outra tela.
                if not (
                    ctypes.windll.user32.GetAsyncKeyState(
                        0x01
                    ) & 0x8000
                ):
                    self._finish_compact_drag()
                    return

            except Exception:
                pass

        mouse_x, mouse_y = (
            self._win32_cursor_pos()
        )

        if self._compact_drag_start:
            sx, sy = self._compact_drag_start

            dist = (
                abs(mouse_x - sx)
                + abs(mouse_y - sy)
            )

            if dist > 4:
                self._dragging = True
                self._drag_dist = dist

        left, top, right, bottom = (
            self._win32_workarea_from_point(
                mouse_x,
                mouse_y
            )
        )

        x = (
            mouse_x
            - self._compact_drag_offset_x
        )

        x = max(
            left,
            min(
                x,
                right - self.COMPACT_W
            )
        )

        y = (
            bottom - self.COMPACT_H
        )

        self._win32_move_resize(
            x,
            y,
            self.COMPACT_W,
            self.COMPACT_H
        )

        self.root.after(
            16,
            self._compact_drag_tick
        )


    # ── Sprites ────────────────────────────────────────────────────────────────

    def _normal_sprite_size(self):
        percentual = int(
            cfg.get("tamanho_normal", 100)
        )

        percentual = max(
            60,
            min(120, percentual)
        )

        return max(
            1,
            int(150 * percentual / 100)
        )


    def _compact_sprite_scale(self):
        percentual = int(
            cfg.get("tamanho_compacto", 85)
        )

        percentual = max(
            60,
            min(120, percentual)
        )

        return percentual / 100.0


    def _reload_sprites(self):
        self._idle_frames = self._load_idle_frames()
        self._alert_frames = self._load_alert_frames()
        self._waiting_frames = self._load_waiting_frames()
        self._happy_frame = self._load_happy_frame()
        self._compact_frames = self._load_compact_frames()
        self._yawn_frames = self._load_yawn_frames()

        self._alert_frame_index = 0
        self._compact_frame_index = 0


    def _load_idle_frames(self):
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "idle"
        )

        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
        ]

        frames = []

        for arquivo in arquivos:
            if not arquivo.exists():
                print(f"[MARVIN] Sprite nao encontrado: {arquivo}")
                continue

            imagem = Image.open(arquivo).convert("RGBA")

            tamanho = self._normal_sprite_size()

            imagem = imagem.resize(
                (tamanho, tamanho),
                Image.Resampling.NEAREST
            )

            frame = ImageTk.PhotoImage(imagem)
            frames.append(frame)

        print(
            f"[MARVIN] {len(frames)} frame(s) idle carregado(s)."
        )

        return frames

    def _load_alert_frames(self):
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "alert"
        )

        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
        ]

        frames = []

        for arquivo in arquivos:
            if not arquivo.exists():
                print(f"[MARVIN] Sprite de alerta nao encontrado: {arquivo}")
                continue

            imagem = Image.open(arquivo).convert("RGBA")

            tamanho = self._normal_sprite_size()

            imagem = imagem.resize(
                (tamanho, tamanho),
                Image.Resampling.NEAREST
            )

            frame = ImageTk.PhotoImage(imagem)
            frames.append(frame)

        print(
            f"[MARVIN] {len(frames)} frame(s) alert carregado(s)."
        )

        return frames


    def _load_waiting_frames(self):
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "waiting"
        )

        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
            pasta / "03.png",
        ]

        frames = []

        for arquivo in arquivos:
            if not arquivo.exists():
                print(
                    f"[MARVIN] Sprite waiting nao encontrado: {arquivo}"
                )
                continue

            imagem = Image.open(
                arquivo
            ).convert("RGBA")

            tamanho = self._normal_sprite_size()

            imagem = imagem.resize(
                (tamanho, tamanho),
                Image.Resampling.NEAREST
            )

            frames.append(
                ImageTk.PhotoImage(imagem)
            )

        print(
            f"[MARVIN] {len(frames)} frame(s) waiting carregado(s)."
        )

        return frames


    def _load_yawn_frames(self):
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "yawn"
        )

        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
        ]

        frames = []

        for arquivo in arquivos:
            if not arquivo.exists():
                print(f"[MARVIN] Sprite yawn nao encontrado: {arquivo}")
                continue

            imagem = Image.open(arquivo).convert("RGBA")

            tamanho = self._normal_sprite_size()

            imagem = imagem.resize(
                (tamanho, tamanho),
                Image.Resampling.NEAREST
            )

            frames.append(
                ImageTk.PhotoImage(imagem)
            )

        print(
            f"[MARVIN] {len(frames)} frame(s) yawn carregado(s)."
        )

        return frames


    def _load_compact_frames(self):
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "compact"
        )

        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
            pasta / "03.png",
        ]

        imagens = []

        for arquivo in arquivos:
            if not arquivo.exists():
                print(
                    f"[MARVIN] Sprite compact nao encontrado: {arquivo}"
                )
                continue

            imagens.append(
                Image.open(arquivo).convert("RGBA")
            )

        if not imagens:
            return []

        # Descobre uma area comum envolvendo todos os pixels visiveis.
        caixas = []

        for imagem in imagens:
            bbox = imagem.getchannel("A").getbbox()

            if bbox:
                caixas.append(bbox)

        if not caixas:
            return []

        left = min(b[0] for b in caixas)
        top = min(b[1] for b in caixas)
        right = max(b[2] for b in caixas)
        bottom = max(b[3] for b in caixas)

        crop_box = (left, top, right, bottom)

        largura = right - left
        altura = bottom - top

        compact_scale = self._compact_sprite_scale()

        max_w = max(
            1,
            int(92 * compact_scale)
        )

        max_h = max(
            1,
            int(64 * compact_scale)
        )

        escala = min(
            max_w / largura,
            max_h / altura
        )

        novo_w = max(1, int(largura * escala))
        novo_h = max(1, int(altura * escala))

        frames = []

        for imagem in imagens:
            imagem = imagem.crop(crop_box)

            imagem = imagem.resize(
                (novo_w, novo_h),
                Image.Resampling.NEAREST
            )

            frames.append(
                ImageTk.PhotoImage(imagem)
            )

        print(
            f"[MARVIN] {len(frames)} frame(s) compact carregado(s)."
        )

        return frames


    def _load_happy_frame(self):
        arquivo = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / "happy"
            / "01.png"
        )

        if not arquivo.exists():
            print(f"[MARVIN] Sprite happy nao encontrado: {arquivo}")
            return None

        imagem = Image.open(arquivo).convert("RGBA")
        tamanho = self._normal_sprite_size()

        imagem = imagem.resize(
            (tamanho, tamanho),
            Image.Resampling.NEAREST
        )

        frame = ImageTk.PhotoImage(imagem)

        print("[MARVIN] frame happy carregado.")

        return frame


    def _draw_idle_sprite(self):
        if not self._idle_frames:
            return None

        now = time.monotonic()

        # Comeca uma piscada nova
        if now >= self._next_blink and now >= self._blink_until:
            self._blink_until = now + 0.14
            self._next_blink = now + random.uniform(self.BLINK_MIN_SECONDS, self.BLINK_MAX_SECONDS)

        # Frame 02 enquanto estiver piscando
        if (
            now < self._blink_until
            and len(self._idle_frames) >= 2
        ):
            frame = self._idle_frames[1]

        # Frame 01 normalmente
        else:
            frame = self._idle_frames[0]

        self.cv.delete("all")

        bob = int(math.sin(self.t * 1.4) * 3)

        x = self.W // 2
        bottom_y = self.H - 8 + bob

        sprite_w = frame.width()
        sprite_h = frame.height()

        top_y = bottom_y - sprite_h

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return top_y

    def _draw_yawn_sprite(self):
        if len(self._yawn_frames) < 2:
            self.state = "idle"
            self._next_yawn = (
                time.monotonic()
                + random.uniform(self.YAWN_MIN_SECONDS, self.YAWN_MAX_SECONDS)
            )
            return self._draw_idle_sprite()

        now = time.monotonic()

        if self._yawn_last_frame == 0.0:
            self._yawn_last_frame = now

        # Troca de frame
        if now - self._yawn_last_frame >= 0.32:
            self._yawn_index += 1
            self._yawn_last_frame = now

        # Terminou o bocejo
        if self._yawn_index >= len(self._yawn_sequence):
            self.state = "idle"
            self._yawn_index = 0
            self._yawn_last_frame = 0.0

            self._next_yawn = (
                now + random.uniform(self.YAWN_MIN_SECONDS, self.YAWN_MAX_SECONDS)
            )

            return self._draw_idle_sprite()

        indice = self._yawn_sequence[self._yawn_index]
        frame = self._yawn_frames[indice]

        self.cv.delete("all")

        bob = int(math.sin(self.t * 1.4) * 3)

        x = self.W // 2
        bottom_y = self.H - 8 + bob
        top_y = bottom_y - frame.height()

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return top_y


    def _draw_happy_sprite(self):
        if self._happy_frame is None:
            return None

        frame = self._happy_frame

        self.cv.delete("all")

        bob = int(math.sin(self.t * 1.4) * 3)

        x = self.W // 2
        bottom_y = self.H - 8 + bob
        top_y = bottom_y - frame.height()

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return top_y


    def _draw_alert_sprite(self):
        if not self._alert_frames:
            return None

        now = time.monotonic()

        # Troca de frame aproximadamente a cada 180 ms
        if now - self._alert_last_frame >= self.ALERT_FRAME_SECONDS:
            self._alert_frame_index = (
                self._alert_frame_index + 1
            ) % len(self._alert_frames)

            self._alert_last_frame = now

        frame = self._alert_frames[self._alert_frame_index]

        self.cv.delete("all")

        bob = int(math.sin(self.t * 1.4) * 3)

        x = self.W // 2
        bottom_y = self.H - 8 + bob

        sprite_h = frame.height()

        top_y = bottom_y - sprite_h

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return top_y


    def _draw_waiting_sprite(self, indice):
        if not self._waiting_frames:
            return self._draw_alert_sprite()

        indice = max(
            0,
            min(
                indice,
                len(self._waiting_frames) - 1
            )
        )

        frame = self._waiting_frames[indice]

        self.cv.delete("all")

        bob = int(
            math.sin(self.t * 1.4) * 3
        )

        x = self.W // 2
        bottom_y = self.H - 8 + bob
        top_y = bottom_y - frame.height()

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return top_y


    def _update_waiting_reaction(self):
        """Atualiza a fala enquanto o lembrete e ignorado."""

        if (
            not self._reminder_queue
            or self._bubble_mode != "alert"
            or self._reminder_started_at is None
        ):
            return

        tempo = (
            time.monotonic()
            - self._reminder_started_at
        )

        t1, t2, t3 = self.WAITING_TIMES

        if tempo >= t3:
            stage = 3

        elif tempo >= t2:
            stage = 2

        elif tempo >= t1:
            stage = 1

        else:
            stage = 0

        if (
            stage
            == self._waiting_reaction_stage
        ):
            return

        self._waiting_reaction_stage = stage

        if stage == 0:
            return

        tarefa = (
            self._reminder_queue[0][1]
        )

        defaults = [
            "Ei... {tarefa}",
            "Vai fazer ou adiar? {tarefa}",
            "Ainda estou esperando: {tarefa}",
        ]

        frases = cfg.get(
            "frases_waiting",
            defaults
        )

        if (
            not isinstance(frases, list)
            or len(frases) < 3
        ):
            frases = defaults

        try:
            frase = str(
                frases[stage - 1]
            ).strip()
        except Exception:
            frase = defaults[
                stage - 1
            ]

        if not frase:
            frase = defaults[
                stage - 1
            ]

        # Substitui apenas nosso marcador.
        # Outros caracteres { } permanecem intactos.
        self.bubble = frase.replace(
            "{tarefa}",
            tarefa
        )


    def _draw_reminder_sprite(self):
        """
        Escolhe o sprite do lembrete conforme
        o tempo que o usuario esta sem responder.
        """

        # Se o usuario ja abriu o menu de adiar,
        # ele ja respondeu ao alerta.
        if self._bubble_mode != "alert":
            return self._draw_alert_sprite()

        if self._reminder_started_at is None:
            return self._draw_alert_sprite()

        if not self._waiting_frames:
            return self._draw_alert_sprite()

        tempo = (
            time.monotonic()
            - self._reminder_started_at
        )

        t1, t2, t3 = self.WAITING_TIMES

        # 2 minutos ou mais
        if tempo >= t3:
            return self._draw_waiting_sprite(2)

        # 1 minuto e 30 segundos
        if tempo >= t2:
            return self._draw_waiting_sprite(1)

        # 1 minuto
        if tempo >= t1:
            return self._draw_waiting_sprite(0)

        # Antes de 1 minuto continua usando
        # a animacao normal de alerta.
        return self._draw_alert_sprite()


    def _draw_compact_sprite(self):
        if not self._compact_frames:
            return None

        now = time.monotonic()

        # 01 -> 02 -> 03 -> 02 -> ...
        if now - self._compact_last_frame >= self.COMPACT_FRAME_SECONDS:
            self._compact_frame_index = (
                self._compact_frame_index + 1
            ) % len(self._compact_sequence)

            self._compact_last_frame = now

        indice = self._compact_sequence[
            self._compact_frame_index
        ]

        indice = min(
            indice,
            len(self._compact_frames) - 1
        )

        frame = self._compact_frames[indice]

        self.cv.delete("all")

        # Janela compacta real.
        x = self.COMPACT_W // 2

        # 1 px acima da borda inferior:
        # visualmente fica encostado na barra
        # sem cortar o sprite.
        bottom_y = self.COMPACT_H - 1

        self.cv.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s"
        )

        return bottom_y - frame.height()


    # ── Nao Perturbe ─────────────────────────────────────────────────────────

    def _np_label(self):
        if self._compact_enabled:
            return "Mostrar MARVIN"

        return "Modo compacto"

    def _toggle_np(self):
        ativando = not self._compact_enabled

        self._compact_enabled = ativando

        self.bubble = ""
        self.b_timer = 0
        self._bubble_mode = "normal"
        self._bubble_hover = None
        self.state = "idle"

        self._compact_frame_index = 0
        self._compact_last_frame = time.monotonic()

        if ativando:
            # Durante lembrete, apenas guarda
            # a preferencia para voltar depois.
            if not self._reminder_queue:
                self._enter_compact_layout(
                    remember_normal=True
                )

        else:
            if self._compact_mode:
                self._restore_normal_layout()

        self.ctx.entryconfig(
            3,
            label=self._np_label()
        )

        if self._tray_icon is not None:
            try:
                self._tray_icon.update_menu()
            except Exception:
                pass


    # ── Resumo do dia ───────────────────────────────────────────────────────

    def _task_due_today(self, row, hoje):
        """
        Diz se uma tarefa pendente pertence ao dia atual,
        considerando a recorrencia.
        """

        try:
            (
                tid,
                texto,
                desc,
                data,
                hora,
                rep,
                concluida,
                lembrado
            ) = row

        except Exception:
            return False

        if concluida:
            return False

        try:
            data_base = datetime.date.fromisoformat(
                data
            )
        except Exception:
            return False

        # A recorrencia ainda nao comecou.
        if data_base > hoje:
            return False

        if rep == "Nunca":
            return data_base == hoje

        if rep == "Todo dia":
            return True

        if rep == "Toda semana":
            return (
                data_base.weekday()
                == hoje.weekday()
            )

        if rep == "Seg/Qua/Sex":
            return hoje.weekday() in (
                0,
                2,
                4
            )

        if rep == "Seg a Sex":
            return hoje.weekday() < 5

        if rep == "Fins de semana":
            return hoje.weekday() >= 5

        return False


    def _inicio_do_dia(self):
        """
        Na primeira abertura do MARVIN no dia,
        mostra o resumo. Nas proximas aberturas,
        usa apenas a saudacao normal.
        """

        hoje = (
            datetime.date.today()
            .isoformat()
        )

        if (
            cfg.get("ultimo_resumo_dia")
            != hoje
        ):
            self._resumo_do_dia()

        else:
            self._saudacao_inicial()


    def _resumo_do_dia(self):
        # Nunca substitui um lembrete ativo.
        if self._reminder_queue:
            return

        # Se estiver escondido, reaparece.
        self._show_marvin()

        # Se estiver compacto, expande
        # temporariamente para mostrar o balao.
        if self._compact_mode:
            self._expand_compact_for_reminder()

        hoje = datetime.date.today()
        hoje_iso = hoje.isoformat()

        try:
            rows = db_listar()
        except Exception as exc:
            print(
                f"[MARVIN] Erro ao gerar resumo: {exc}"
            )
            return

        pendentes_hoje = 0
        atrasadas = 0

        for row in rows:
            try:
                (
                    tid,
                    texto,
                    desc,
                    data,
                    hora,
                    rep,
                    concluida,
                    lembrado
                ) = row

            except Exception:
                continue

            if concluida:
                continue

            if self._task_due_today(
                row,
                hoje
            ):
                pendentes_hoje += 1
                continue

            # Apenas tarefas sem recorrencia
            # sao consideradas atrasadas.
            if rep == "Nunca":
                try:
                    data_tarefa = (
                        datetime.date.fromisoformat(
                            data
                        )
                    )

                    if data_tarefa < hoje:
                        atrasadas += 1

                except Exception:
                    pass

        concluidas_hoje = (
            db_streak_hoje()
        )

        hora = (
            datetime.datetime.now().hour
        )

        if hora < 12:
            saudacao = "Bom dia!"

        elif hora < 18:
            saudacao = "Boa tarde!"

        else:
            saudacao = "Boa noite!"

        partes = []

        if pendentes_hoje == 0:
            partes.append(
                "Nenhuma tarefa pendente para hoje."
            )

        elif pendentes_hoje == 1:
            partes.append(
                "Voce tem 1 tarefa para hoje."
            )

        else:
            partes.append(
                f"Voce tem {pendentes_hoje} tarefas para hoje."
            )

        if atrasadas == 1:
            partes.append(
                "1 esta atrasada."
            )

        elif atrasadas > 1:
            partes.append(
                f"{atrasadas} estao atrasadas."
            )

        if concluidas_hoje == 1:
            partes.append(
                "1 concluida hoje."
            )

        elif concluidas_hoje > 1:
            partes.append(
                f"{concluidas_hoje} concluidas hoje."
            )

        mensagem = (
            saudacao
            + " "
            + " ".join(partes)
        )

        cfg["ultimo_resumo_dia"] = (
            hoje_iso
        )

        save_cfg(cfg)

        self._bubble_mode = "normal"
        self._bubble_hover = None

        self.say(
            mensagem,
            "talking",
            8000
        )


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
            self._bubble_mode = "normal"
            self._bubble_hover = None
            self.say(
                random.choice(_frases_idle_ativas()),
                "talking",
                10000
            )
        self._schedule_idle()

    # ── Fala ──────────────────────────────────────────────────────────────────

    def say(self, text, state="talking", duration=4000):
        self.bubble = text
        self.state = state

        try:
            duration = max(
                0,
                float(duration)
            )
        except (TypeError, ValueError):
            duration = 0

        self.b_timer = duration

        if duration > 0:
            self._bubble_deadline = (
                time.monotonic()
                + duration / 1000.0
            )
        else:
            self._bubble_deadline = None

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

        # Se houver outro lembrete na fila,
        # mantem o proximo alerta visivel.
        if self._reminder_queue:
            return

        # Caso contrario, comemora por 3 segundos.
        self.say(msg, "happy", 2000)

    def _next_reminder(self):
        if self._reminder_queue:
            self._reminder_queue.pop(0)

        if self._reminder_queue:
            nxt = self._reminder_queue[0]

            # A proxima tarefa acabou de virar o alerta ativo.
            if cfg.get("som", True):
                _beep()

            # Nova tarefa = novo contador de espera.
            self._reminder_started_at = time.monotonic()
            self._waiting_reaction_stage = 0

            self.state = "alert"
            self.b_timer = 0
            self.bubble = f"Hora de: {nxt[1]}"

            self._bubble_mode = "alert"
            self._bubble_hover = None

        else:
            self._reminder_started_at = None
            self._waiting_reaction_stage = 0
            self.state = "idle"
            self.bubble = ""
            self.b_timer = 0

            self._bubble_mode = "normal"
            self._bubble_hover = None

    # ── Animacao ──────────────────────────────────────────────────────────────

    def _animate(self):
        self.t += 0.05

        # Se o usuario escolheu modo compacto e nao existe mais
        # nenhum alerta/fala, volta automaticamente para a cabeca.
        if (
            self._compact_enabled
            and not self._compact_mode
            and not self._reminder_queue
            and self.state == "idle"
            and not self.bubble
        ):
            self._compact_frame_index = 0
            self._compact_last_frame = time.monotonic()

            self._enter_compact_layout(
                remember_normal=False
            )

        # Modo compacto: somente desenha os frames da cabeca.
        if self._compact_mode:
            self._draw_compact_sprite()
            self.root.after(self.ANIMATION_TICK_MS, self._animate)
            return

        now = time.monotonic()

        self._update_waiting_reaction()

        # Bocejo aleatorio somente quando MARVIN esta livre
        if (
            self.state == "idle"
            and not self.bubble
            and not self._reminder_queue
            and self._yawn_frames
            and now >= self._next_yawn
        ):
            self.state = "yawn"
            self._yawn_index = 0
            self._yawn_last_frame = now
        if self.b_timer > 0:

            # Usa relogio monotonic em vez de assumir
            # que cada frame levou exatamente 50 ms.
            if self._bubble_deadline is None:
                self._bubble_deadline = (
                    now
                    + float(self.b_timer) / 1000.0
                )

            restante_ms = max(
                0.0,
                (
                    self._bubble_deadline
                    - now
                ) * 1000.0
            )

            self.b_timer = restante_ms

            if restante_ms <= 0:
                self._bubble_deadline = None

                # Nunca fecha automaticamente um lembrete.
                if self._reminder_queue:
                    self.b_timer = 0

                # Baloes normais continuam fechando pelo tempo.
                else:
                    self.b_timer = 0
                    self.bubble = ""
                    self.state = "idle"

        # Sprite de lembrete.
        # Depois de algum tempo sem resposta,
        # troca progressivamente para os sprites waiting.
        if (
            self.state == "alert"
            and (
                self._alert_frames
                or self._waiting_frames
            )
        ):
            top_y = self._draw_reminder_sprite()

        # Sprite feliz
        elif (
            self.state == "happy"
            and self._happy_frame is not None
        ):
            top_y = self._draw_happy_sprite()

        # Bocejo
        elif (
            self.state == "yawn"
            and self._yawn_frames
        ):
            top_y = self._draw_yawn_sprite()

        # Sprite normal
        elif (
            self.state in ("idle", "talking")
            and self._idle_frames
        ):
            top_y = self._draw_idle_sprite()

        # Fallback caso nenhum sprite PNG esteja disponivel.
        else:
            self.cv.delete("all")
            top_y = self.H - 8

        if self.bubble:
            draw_bubble(
                self.cv,
                self.t,
                self.W // 2,
                top_y,
                self.bubble,
                self.W,
                mode=self._bubble_mode,
                hover=self._bubble_hover
            )

        self.root.after(self.ANIMATION_TICK_MS, self._animate)

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _drag_start(self, e):
        self._dx, self._dy = e.x, e.y
        self._drag_dist = 0

        if self._compact_mode:
            mouse_x, mouse_y = (
                self._win32_cursor_pos()
            )

            rect = self._win32_window_rect()

            self._compact_drag_offset_x = (
                mouse_x - rect[0]
            )

            self._compact_drag_start = (
                mouse_x,
                mouse_y
            )

            self._compact_drag_active = True

            self._compact_drag_tick()


    def _drag_move(self, e):
        # Compacto usa o loop global do Windows.
        if self._compact_mode:
            return

        dx = e.x - self._dx
        dy = e.y - self._dy

        self._drag_dist += (
            abs(dx) + abs(dy)
        )

        if self._drag_dist > 4:
            self._dragging = True

        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy

        self.root.geometry(
            f"+{x}+{y}"
        )


    def _bubble_button_at(self, x, y):
        """
        Retorna qual botão do balão está na posição x/y.
        Retorna None quando não existe botão nessa posição.
        """

        if self._bubble_mode not in ("alert", "snooze"):
            return None

        if not self.bubble:
            return None

        # Usa a altura REAL do sprite de alerta.
        # Isso mantem a area clicavel exatamente no mesmo lugar
        # do balao, mesmo quando o tamanho do MARVIN e alterado.
        bob = int(math.sin(self.t * 1.4) * 3)

        if self._alert_frames:
            sprite_h = self._alert_frames[0].height()

            top_y = (
                self.H
                - 8
                + bob
                - sprite_h
            )
        elif self._waiting_frames:
            sprite_h = self._waiting_frames[0].height()

            top_y = (
                self.H
                - 8
                + bob
                - sprite_h
            )

        else:
            # Nenhum sprite disponivel.
            top_y = self.H - 8 + bob

        layout = _bubble_layout(
            self.bubble,
            self.W,
            self.W // 2,
            top_y,
            self._bubble_mode
        )

        if layout is None:
            return None

        bx = layout["bx"]
        bw = layout["bw"]
        button_y = layout["button_y"]

        if self._bubble_mode == "alert":

            complete_x = layout["complete_x"]
            snooze_x = layout["snooze_x"]

            if (
                (x - complete_x) ** 2
                + (y - (button_y + 11)) ** 2
                <= 16 ** 2
            ):
                return "complete"

            if (
                (x - snooze_x) ** 2
                + (y - (button_y + 11)) ** 2
                <= 16 ** 2
            ):
                return "snooze"

        elif self._bubble_mode == "snooze":

            for value, x_button in (
                layout["option_x"].items()
            ):

                if (
                    (x - x_button) ** 2
                    + (y - (button_y + 12)) ** 2
                    <= 18 ** 2
                ):
                    return value

            back_y = layout["back_y"]

            if (
                abs(x - (bx + bw // 2)) <= 45
                and abs(y - back_y) <= 12
            ):
                return "back"

        return None

    def _drag_end(self, e):
        if self._compact_mode:
            self._compact_drag_active = False
            self._compact_drag_start = None
            self._save_compact_position()

        else:
            cfg["pos_x"] = self.root.winfo_x()
            cfg["pos_y"] = self.root.winfo_y()

            self._normal_pos = (
                cfg["pos_x"],
                cfg["pos_y"]
            )

            save_cfg(cfg)

        if not self._dragging:
            button = self._bubble_button_at(e.x, e.y)

            if button == "complete":
                self.complete_task()

            elif button == "snooze":
                # O usuario respondeu ao alerta.
                # A escolha do tempo agora acontece
                # na janela moderna de adiamento.
                self._reminder_started_at = None
                self._waiting_reaction_stage = 0
                self._bubble_hover = None

                task = self.reminded_task

                if task:
                    SnoozeWindow(
                        self.root,
                        self,
                        task
                    )

            elif button in ("5", "15", "30", "60"):
                task = self.reminded_task

                if task:
                    from datetime import datetime, timedelta

                    minutos = int(button)
                    novo_horario = datetime.now() + timedelta(minutes=minutos)

                    nova_data = novo_horario.strftime("%Y-%m-%d")
                    nova_hora = novo_horario.strftime("%H:%M")

                    db_adiar(
                        task[0],
                        nova_data,
                        nova_hora
                    )

                    self._bubble_mode = "normal"
                    self._bubble_hover = None
                    self._next_reminder()

            elif button == "back":
                # Voltou sem escolher adiamento:
                # comeca novamente a contar a espera.
                self._reminder_started_at = time.monotonic()
                self._waiting_reaction_stage = 0

                self._bubble_mode = "alert"
                self._bubble_hover = None

            else:
                # Clique esquerdo comum:
                # abre o painel somente quando nao existe lembrete ativo.
                if (
                    self._bubble_mode == "normal"
                    and not self._reminder_queue
                ):
                    self._on_click()

        self._dragging = False
        self._drag_dist = 0

    def _on_click(self):
        # Durante alertas, toda interacao acontece no proprio balao.
        if self._bubble_mode in ("alert", "snooze"):
            return

        if self._reminder_queue:
            return

        if self._panel_open:
            return

        self._panel_open = True

        try:
            panel = InteractionPanel(
                self.root,
                self,
                mode="idle"
            )

        except Exception as exc:
            # Se a criacao do painel falhar, libera
            # imediatamente novos cliques no MARVIN.
            self._panel_open = False

            print(
                f"[MARVIN] Erro ao abrir InteractionPanel: {exc}"
            )

            return

        panel.win.bind(
            "<Destroy>",
            lambda e: setattr(
                self,
                "_panel_open",
                False
            )
        )

    def _show_menu(self, e):
        try:
            self.ctx.tk_popup(e.x_root, e.y_root)
        finally:
            self.ctx.grab_release()

 

    # ── Lembretes ─────────────────────────────────────────────────────────────

    def _start_reminders(self):
        # Evita criar duas threads de lembretes
        # para a mesma instancia do MARVIN.
        if (
            self._reminder_thread is not None
            and self._reminder_thread.is_alive()
        ):
            return

        self._reminder_stop.clear()

        def loop():
            # Event.wait substitui time.sleep.
            # Alem de esperar 1 segundo, ele acorda
            # imediatamente quando o MARVIN e encerrado.
            while not self._reminder_stop.wait(self.REMINDER_POLL_SECONDS):

                now = datetime.datetime.now()
                today = now.strftime("%Y-%m-%d")

                try:
                    rows = db_listar(
                        apenas_pendentes=True
                    )
                except Exception as exc:
                    print(
                        f"[MARVIN] Erro ao listar lembretes: {exc}"
                    )
                    continue

                for row in rows:

                    if self._reminder_stop.is_set():
                        break

                    (
                        tid,
                        texto,
                        desc,
                        data,
                        hora,
                        rep,
                        conc,
                        lemb
                    ) = row

                    if lemb:
                        continue

                    hora_s = hora[:5]

                    try:
                        data_original = (
                            datetime.date.fromisoformat(data)
                        )
                    except (TypeError, ValueError):
                        continue

                    hoje_data = now.date()

                    if hoje_data < data_original:
                        continue

                    if rep == "Nunca":
                        data_lembrete = data_original

                    else:
                        if not self._should_remind(
                            rep,
                            data,
                            now,
                            today
                        ):
                            continue

                        data_lembrete = hoje_data

                    try:
                        hora_obj = datetime.datetime.strptime(
                            hora_s,
                            "%H:%M"
                        ).time()
                    except (TypeError, ValueError):
                        continue

                    task_dt = datetime.datetime.combine(
                        data_lembrete,
                        hora_obj
                    )

                    diff = (
                        now - task_dt
                    ).total_seconds()

                    if (
                        0 <= diff < 90
                        and not self._reminder_stop.is_set()
                    ):
                        try:
                            self.root.after(
                                0,
                                lambda r=row: self._enqueue(r)
                            )
                        except tk.TclError:
                            return

        self._reminder_thread = threading.Thread(
            target=loop,
            name="marvin-reminders",
            daemon=True
        )

        self._reminder_thread.start()

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

        # Evita colocar a mesma tarefa duas vezes na fila
        if any(r[0] == tid for r in self._reminder_queue):
            return

        db_marcar_lembrado(tid)

        # Tarefas recorrentes podem ser lembradas novamente
        if rep != "Nunca":
            self.root.after(
                self.RECURRENT_REMINDER_RESET_MS,
                lambda i=tid: db_reset_lembrado(i)
            )

        # Se o usuario estiver usando modo compacto,
        # mostra temporariamente o MARVIN inteiro durante o alerta.
        # A preferencia _compact_enabled continua ativa.
        if (
            self._compact_enabled
            and self._compact_mode
        ):
            self._expand_compact_for_reminder()

        # Se ja existe um alerta na tela,
        # apenas adiciona esta tarefa na fila.
        was_empty = not self._reminder_queue

        self._reminder_queue.append(row)

        if not was_empty:
            return

        # Se estava escondido, reaparece para o lembrete.
        self._show_marvin()

        # Som do lembrete.
        if cfg.get("som", True):
            _beep()

        # Comeca agora a contar quanto tempo
        # o usuario demora para responder.
        self._reminder_started_at = time.monotonic()
        self._waiting_reaction_stage = 0
        
        self._bubble_mode = "alert"
        self._bubble_hover = None
        self.state = "alert"

        # Lembretes nao possuem tempo para desaparecer.
        # Ficam visiveis ate concluir ou adiar.
        self.b_timer = 0
        self.bubble = f"Hora de: {row[1]}"

    def _on_close(self):
        """Encerra completamente o MARVIN."""

        # Avisa imediatamente a thread de lembretes
        # que o aplicativo esta sendo encerrado.
        try:
            self._reminder_stop.set()
        except Exception:
            pass

        try:
            if self._compact_mode:
                self._save_compact_position()
            else:
                cfg["pos_x"] = self.root.winfo_x()
                cfg["pos_y"] = self.root.winfo_y()
                save_cfg(cfg)
        except Exception:
            pass

        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass

            self._tray_icon = None

        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()

# =============================================================================
if __name__ == "__main__":
    MarvinCompanion().run()





