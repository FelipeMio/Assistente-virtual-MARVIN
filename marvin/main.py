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
from .notifications import NotificationManager
from .checklist import abrir_checklist
from .ui.home import abrir_home
from .ui.settings import SettingsWindow as SettingsWindowUI
from .ui.snooze import SnoozeWindow
from .ui.interaction_panel import InteractionPanel as InteractionPanelUI
from .ui.waiting_phrases import WaitingPhrasesWindow as WaitingPhrasesWindowUI
from .ui.edit_task import EditTaskWindow as EditTaskWindowUI
from .ui.new_task import NewTaskWindow as NewTaskWindowUI
from .ui.task_list import TaskWindow as TaskWindowUI

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
    
    "Clique com botao direito para o menu.",
  
    
]

IDLE_FREQUENCY_OPTIONS = {
    "Nunca": 0,
    "1 minuto": 60,
    "5 minutos": 300,
    "15 minutos": 900,
    "30 minutos": 1800,
}


def _idle_frequency_label(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        seconds = 300

    for label, value in (
        IDLE_FREQUENCY_OPTIONS.items()
    ):
        if value == seconds:
            return label

    return "5 minutos"


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
    "Nenhuma",
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

def NewTaskWindow(
    parent,
    companion,
    prefill="",
):
    """
    Abre a janela de nova tarefa
    implementada em marvin.ui.new_task.
    """
    return NewTaskWindowUI(
        parent,
        companion,
        prefill,
        config=cfg,
        palette_factory=get_modern_palette,
        positioner=_position_near_marvin,
        repeat_options=REPEAT_OPTS,
        bind_auto_time=_bind_auto_time,
        validate_date=_validate_date,
        validate_time=_validate_time,
        db_create=db_criar,
    )


#  JANELA: LISTA DE TAREFAS

def TaskWindow(
    parent,
    companion,
):
    """
    Abre a lista de tarefas implementada
    em marvin.ui.task_list.
    """
    return TaskWindowUI(
        parent,
        companion,
        config=cfg,
        palette_factory=get_modern_palette,
        positioner=_position_near_marvin,
        new_task_factory=NewTaskWindow,
        edit_task_factory=EditTaskWindow,
        db_list_prioritized=(
            db_listar_com_prioridade
        ),
        db_list=db_listar,
        db_complete=db_concluir,
        db_uncomplete=db_desconcluir,
        db_delete=db_excluir,
    )


def EditTaskWindow(
    parent,
    companion,
    tid,
    callback,
):
    """
    Abre a janela de edicao de tarefa
    implementada em marvin.ui.edit_task.
    """
    return EditTaskWindowUI(
        parent,
        companion,
        tid,
        callback,
        config=cfg,
        positioner=_position_near_marvin,
        repeat_options=REPEAT_OPTS,
        priority_options=PRIORITY_OPTS,
        bind_auto_time=_bind_auto_time,
        validate_time=_validate_time,
        validate_date=_validate_date,
        db_get=db_obter,
        db_update=db_alterar,
    )


#  JANELA: FRASES DE ESPERA

def WaitingPhrasesWindow(
    parent,
    companion,
):
    """
    Abre a janela de frases de espera
    implementada em marvin.ui.waiting_phrases.
    """
    return WaitingPhrasesWindowUI(
        parent,
        companion,
        config=cfg,
        positioner=_position_near_marvin,
        save_config=save_cfg,
    )


#  JANELA: CONFIGURACOES

def SettingsWindow(
    parent,
    companion,
):
    """
    Abre a janela de configuracoes implementada
    em marvin.ui.settings.
    """
    return SettingsWindowUI(
        parent,
        companion,
        config=cfg,
        positioner=_position_near_marvin,
        startup_enabled=_startup_enabled,
        set_startup_enabled=(
            _set_startup_enabled
        ),
        idle_frequency_options=(
            IDLE_FREQUENCY_OPTIONS
        ),
        idle_frequency_label=(
            _idle_frequency_label
        ),
        idle_msgs=_IDLE_MSGS,
        waiting_phrases_factory=(
            WaitingPhrasesWindow
        ),
        db_path=DB_F,
        db_cleaner=db_limpar_antigas,
    )


#  JANELA: PAINEL DE INTERACAO

def InteractionPanel(
    root,
    companion,
    mode="idle",
):
    """
    Abre o painel de interacao implementado
    em marvin.ui.interaction_panel.
    """
    return InteractionPanelUI(
        root,
        companion,
        mode=mode,
        settings_factory=SettingsWindow,
        task_factory=TaskWindow,
        new_task_factory=NewTaskWindow,
        snooze_factory=SnoozeWindow,
    )


#  JANELA: ADIAR TAREFA
#  Implementacao em marvin.ui.snooze.


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

        # ID do unico callback pendente do
        # loop de arraste do modo compacto.
        self._compact_drag_job = None

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
        self._idle_job = None
        self._schedule_idle()

        # Eventos
        self.cv.bind("<ButtonPress-1>",   self._drag_start)
        self.cv.bind("<B1-Motion>",       self._drag_move)
        self.cv.bind("<ButtonRelease-1>", self._drag_end)
        self.cv.bind("<Button-3>",         self._on_click)

        # Atualiza o hover dos botoes do balao
        # enquanto o mouse se move.
        self.cv.bind(
            "<Motion>",
            self._on_mouse_motion,
        )

        self.cv.bind(
            "<Leave>",
            self._on_mouse_leave,
        )

        self.root.protocol("WM_DELETE_WINDOW", self._hide_marvin)
        self.root.bind_all("<Control-Shift-N>",
                            lambda e: NewTaskWindow(self.root, self))

        self._start_tray()

        self._animate()
        self._start_reminders()

        # Sistema central de notificacoes do MARVIN.
        self.notifications = NotificationManager()

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

        # Garante que exista apenas um callback
        # de arraste pendente por vez.
        if self._compact_drag_job is not None:
            try:
                self.root.after_cancel(
                    self._compact_drag_job
                )
            except Exception:
                pass

            self._compact_drag_job = None

        if not self._compact_drag_active:
            return

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

        self._compact_drag_job = (
            self.root.after(
                16,
                self._compact_drag_tick,
            )
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


    def _load_frames(
        self,
        subfolder,
        filenames,
        label,
        missing_label=None,
    ):
        """
        Carrega uma sequencia de sprites do MARVIN.

        Todos os frames usam o mesmo tamanho,
        conversao RGBA e redimensionamento NEAREST.
        """
        pasta = (
            Path(__file__).resolve().parent
            / "assets"
            / "marvin"
            / subfolder
        )

        frames = []

        for filename in filenames:
            arquivo = (
                pasta
                / filename
            )

            if not arquivo.exists():
                descricao = (
                    missing_label
                    or f"Sprite {label}"
                )

                print(
                    f"[MARVIN] "
                    f"{descricao} nao encontrado: "
                    f"{arquivo}"
                )
                continue

            imagem = Image.open(
                arquivo
            ).convert(
                "RGBA"
            )

            tamanho = (
                self._normal_sprite_size()
            )

            imagem = imagem.resize(
                (
                    tamanho,
                    tamanho,
                ),
                Image.Resampling.NEAREST,
            )

            frames.append(
                ImageTk.PhotoImage(
                    imagem
                )
            )

        print(
            f"[MARVIN] "
            f"{len(frames)} frame(s) "
            f"{label} carregado(s)."
        )

        return frames


    def _load_idle_frames(self):
        return self._load_frames(
            "idle",
            (
                "01.png",
                "02.png",
            ),
            label="idle",
            missing_label="Sprite",
        )

    def _load_alert_frames(self):
        return self._load_frames(
            "alert",
            (
                "01.png",
                "02.png",
            ),
            label="alert",
            missing_label=(
                "Sprite de alerta"
            ),
        )

    def _load_waiting_frames(self):
        return self._load_frames(
            "waiting",
            (
                "01.png",
                "02.png",
                "03.png",
            ),
            label="waiting",
            missing_label=(
                "Sprite waiting"
            ),
        )

    def _load_yawn_frames(self):
        return self._load_frames(
            "yawn",
            (
                "01.png",
                "02.png",
            ),
            label="yawn",
            missing_label="Sprite yawn",
        )

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

        atual = self._peek_reminder()

        if (
            atual is None
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

        tarefa = atual[1]

        defaults = (
            WaitingPhrasesWindow.DEFAULTS
        )

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

    def _idle_interval_ms(self):
        """
        Retorna o intervalo configurado das
        falas espontaneas em milissegundos.

        Zero significa desativado.
        """
        try:
            seconds = int(
                cfg.get(
                    "idle_interval_seconds",
                    300,
                )
            )
        except (TypeError, ValueError):
            seconds = 300

        return max(
            0,
            seconds,
        ) * 1000


    def _schedule_idle(self):
        """
        Mantem somente um timer idle ativo.
        """

        old_job = getattr(
            self,
            "_idle_job",
            None,
        )

        if old_job is not None:
            try:
                self.root.after_cancel(
                    old_job
                )
            except Exception:
                pass

            self._idle_job = None

        interval = (
            self._idle_interval_ms()
        )

        if interval <= 0:
            return

        self._idle_job = (
            self.root.after(
                interval,
                self._idle_msg,
            )
        )

    def _idle_msg(self):
        self._idle_job = None

        if self._idle_interval_ms() <= 0:
            return

        if (
            self.state == "idle"
            and not self.bubble
        ):
            self._bubble_mode = "normal"
            self._bubble_hover = None

            self.say(
                random.choice(
                    _frases_idle_ativas()
                ),
                "talking",
                10000,
            )

        self._schedule_idle()

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

    def _peek_reminder(self):
        """
        Retorna o lembrete atualmente no topo
        da fila sem remove-lo.
        """
        if not self._reminder_queue:
            return None

        return self._reminder_queue[0]


    @property
    def reminded_task(self):
        return self._peek_reminder()

    def complete_task(self):
        atual = self._peek_reminder()

        if atual is not None:
            db_concluir(
                atual[0]
            )

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

        nxt = self._peek_reminder()

        if nxt is not None:

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


    def _on_mouse_motion(
        self,
        event,
    ):
        # Durante um arraste nao precisamos
        # calcular hover dos botoes do balao.
        if getattr(
            self,
            "_dragging",
            False,
        ):
            return

        hover = self._bubble_button_at(
            event.x,
            event.y,
        )

        if hover != self._bubble_hover:
            self._bubble_hover = hover


    def _on_mouse_leave(
        self,
        event=None,
    ):
        if self._bubble_hover is not None:
            self._bubble_hover = None


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


        self._dragging = False
        self._drag_dist = 0

    def _on_click(self, e=None):
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





