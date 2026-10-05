import tkinter as tk
import customtkinter as ctk
import threading, time, datetime, sys, os
from tkinter import messagebox
from pathlib import Path

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
from .tray import TrayController
from .compact_mode import CompactModeController
from .sprites import SpriteLoader
from .sprite_renderer import SpriteRenderer
from .bubble import BubbleRenderer
from .mouse_interaction import MouseInteractionController
from .reminders import ReminderQueue, ReminderService
from .routine import RoutineController
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

        # Balao de fala e botoes interativos.
        self._bubble_renderer = BubbleRenderer(
            self.cv,
            palette=C,
            normal_size=(
                self.W,
                self.H,
            ),
        )

        # Sprites do MARVIN
        self._sprite_loader = SpriteLoader(
            config=cfg,
        )

        self._sprite_renderer = SpriteRenderer(
            self.cv,
            normal_size=(
                self.W,
                self.H,
            ),
            compact_size=(
                self.COMPACT_W,
                self.COMPACT_H,
            ),
            blink_min_seconds=(
                self.BLINK_MIN_SECONDS
            ),
            blink_max_seconds=(
                self.BLINK_MAX_SECONDS
            ),
            yawn_min_seconds=(
                self.YAWN_MIN_SECONDS
            ),
            yawn_max_seconds=(
                self.YAWN_MAX_SECONDS
            ),
            alert_frame_seconds=(
                self.ALERT_FRAME_SECONDS
            ),
            compact_frame_seconds=(
                self.COMPACT_FRAME_SECONDS
            ),
        )

        self._reload_sprites()

        # Momento em que o lembrete atual apareceu.
        self._reminder_started_at = None

        # Estagio da reacao ao ignorar o lembrete.
        # 0 = normal
        # 1 = waiting 01
        # 2 = waiting 02
        # 3 = waiting 03
        self._waiting_reaction_stage = 0

        # Layout, posicao e drag do modo compacto.
        self._compact = CompactModeController(
            self.root,
            self.cv,
            config=cfg,
            save_config=save_cfg,
            normal_size=(
                self.W,
                self.H,
            ),
            compact_size=(
                self.COMPACT_W,
                self.COMPACT_H,
            ),
            on_drag_distance=(
                self._on_compact_drag_distance
            ),
        )

        # Estado
        self.t               = 0.0
        self.state           = "thinking"
        self.bubble          = ""
        self.b_timer         = 0

        # Monitoramento de lembretes.
        self._reminders = ReminderService(
            self.root,
            list_tasks=db_listar,
            on_due=self._enqueue,
            poll_seconds=(
                self.REMINDER_POLL_SECONDS
            ),
        )

        self._bubble_deadline = None
        self._panel_open = False

        # Bubble interaction state.
        self._bubble_mode = "normal"
        self._bubble_hover = None

        # Mouse interaction.
        self._mouse = MouseInteractionController(
            self.root,
            self.cv,
            config=cfg,
            save_config=save_cfg,
            compact=self._compact,
            compact_mode=lambda:
                self._compact_mode,
            bubble_button_at=lambda x, y:
                self._bubble_renderer.button_at(
                    x,
                    y,
                    t=self.t,
                    text=self.bubble,
                    mode=self._bubble_mode,
                    sprite_height=(
                        self._sprite_renderer
                        .reminder_frame_height()
                    ),
                ),
            get_hover=lambda:
                self._bubble_hover,
            set_hover=lambda value:
                setattr(
                    self,
                    "_bubble_hover",
                    value,
                ),
            on_button=(
                self._handle_bubble_button
            ),
            on_right_click=(
                self._on_click
            ),
        )

        # Bandeja do Windows
        self._is_hidden = False

        self._tray = TrayController(
            self.root,
            on_show=self._show_marvin,
            on_new_task=self._tray_new_task,
            on_home=self._open_home,
            on_toggle_compact=self._toggle_np,
            compact_enabled=lambda:
                self._compact_enabled,
            on_settings=self._tray_settings,
            on_exit=self._on_close,
        )
        
        

        # Rotina diaria e frases idle.
        self._routine = RoutineController(
            self.root,
            config=cfg,
            save_config=save_cfg,
            list_tasks=db_listar,
            streak_today=db_streak_hoje,
            idle_phrases=(
                _frases_idle_ativas
            ),
            greeting_factory=(
                _frase_saudacao
            ),
            say=self.say,
            show_marvin=self._show_marvin,
            reminder_active=lambda:
                bool(
                    self._reminder_queue
                ),
            compact_active=lambda:
                self._compact_mode,
            expand_compact=(
                self._expand_compact_for_reminder
            ),
            can_idle_speak=lambda:
                (
                    self.state == "idle"
                    and not self.bubble
                ),
            set_state=lambda value:
                setattr(
                    self,
                    "state",
                    value,
                ),
            set_bubble_mode=lambda value:
                setattr(
                    self,
                    "_bubble_mode",
                    value,
                ),
            set_bubble_hover=lambda value:
                setattr(
                    self,
                    "_bubble_hover",
                    value,
                ),
        )

        self._routine.schedule_idle()

        # Eventos
        self._mouse.bind()

        self.root.protocol("WM_DELETE_WINDOW", self._hide_marvin)
        self.root.bind_all("<Control-Shift-N>",
                            lambda e: NewTaskWindow(self.root, self))

        self._tray.start()

        self._animate()
        self._reminders.start()

        # Sistema central de notificacoes do MARVIN.
        self.notifications = NotificationManager()

        # Carrega extensoes opcionais instaladas.
        self._extensions = carregar_extensoes(self)

        threading.Thread(target=db_limpar_antigas, daemon=True).start()
        self.root.after(900, self._routine.start_day)

    # ── Bandeja do Windows ─────────────────────────────────────────────────

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
                self._compact.save_position()
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
            abrir_resumo=self._routine.summary,
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
        self._routine.summary()


    def _tray_settings(self):
        self._show_marvin()

        SettingsWindow(
            self.root,
            self
        )


    # ── Modo compacto nativo do Windows ─────────────────────────────────────

    # ========================================================
    # COMPATIBILIDADE DO MODO COMPACTO
    # ========================================================

    @property
    def _compact_enabled(self):
        return self._compact.enabled


    @_compact_enabled.setter
    def _compact_enabled(
        self,
        value,
    ):
        self._compact.enabled = bool(
            value
        )


    @property
    def _compact_mode(self):
        return self._compact.mode


    @_compact_mode.setter
    def _compact_mode(
        self,
        value,
    ):
        self._compact.mode = bool(
            value
        )


    def _expand_compact_for_reminder(
        self,
    ):
        """
        Ponte temporaria para extensoes.
        """
        self._compact.expand_for_reminder()


    def _on_compact_drag_distance(
        self,
        distance,
    ):
        mouse = getattr(
            self,
            "_mouse",
            None,
        )

        if mouse is not None:
            mouse.report_compact_drag_distance(
                distance
            )


    def _reload_sprites(self):
        """
        Recarrega os assets e entrega ao renderer.
        """
        assets = (
            self._sprite_loader
            .load_all()
        )

        self._sprite_renderer.set_assets(
            assets
        )


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

        self._sprite_renderer.reset_compact_animation()

        if ativando:
            # Durante lembrete, apenas guarda
            # a preferencia para voltar depois.
            if not self._reminder_queue:
                self._compact.enter(
                    remember_normal=True
                )

        else:
            if self._compact_mode:
                self._compact.restore()

        try:
            self._tray.update_menu()
        except Exception:
            pass


    # ── Resumo do dia ───────────────────────────────────────────────────────

    def _schedule_idle(self):
        """
        Ponte temporaria usada pela janela
        de configuracoes.
        """
        self._routine.schedule_idle()


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
    def _reminder_queue(self):
        """
        Ponte temporaria para componentes que ainda
        acessam a fila diretamente.
        """
        return self._reminders.queue


    def _peek_reminder(self):
        """
        Retorna o lembrete atualmente no topo
        da fila sem remove-lo.
        """
        return self._reminders.queue.peek()


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
        self._reminders.queue.pop_current()

        nxt = (
            self._reminders.queue.peek()
        )

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

        if (
            self._compact_enabled
            and not self._compact_mode
            and not self._reminder_queue
            and self.state == "idle"
            and not self.bubble
        ):
            self._sprite_renderer.reset_compact_animation()

            self._compact.enter(
                remember_normal=False
            )


        if self._compact_mode:
            self._sprite_renderer.draw_compact()

            self.root.after(
                self.ANIMATION_TICK_MS,
                self._animate,
            )

            return


        now = time.monotonic()

        self._update_waiting_reaction()


        if (
            self.state == "idle"
            and not self.bubble
            and not self._reminder_queue
            and self._sprite_renderer.yawn_due(
                now
            )
        ):
            self.state = "yawn"

            self._sprite_renderer.start_yawn(
                now
            )


        if self.b_timer > 0:

            if self._bubble_deadline is None:
                self._bubble_deadline = (
                    now
                    + float(
                        self.b_timer
                    ) / 1000.0
                )

            restante_ms = max(
                0.0,
                (
                    self._bubble_deadline
                    - now
                ) * 1000.0,
            )

            self.b_timer = restante_ms


            if restante_ms <= 0:
                self._bubble_deadline = None

                if self._reminder_queue:
                    self.b_timer = 0

                else:
                    self.b_timer = 0
                    self.bubble = ""
                    self.state = "idle"


        if (
            self.state == "alert"
            and (
                self._sprite_renderer
                .has_alert_or_waiting
            )
        ):
            top_y = (
                self._sprite_renderer
                .draw_reminder(
                    self.t,
                    bubble_mode=(
                        self._bubble_mode
                    ),
                    reminder_started_at=(
                        self._reminder_started_at
                    ),
                    waiting_times=(
                        self.WAITING_TIMES
                    ),
                )
            )


        elif (
            self.state == "happy"
            and self._sprite_renderer.has_happy
        ):
            top_y = (
                self._sprite_renderer
                .draw_happy(
                    self.t
                )
            )


        elif (
            self.state == "yawn"
            and self._sprite_renderer.has_yawn
        ):
            (
                top_y,
                yawn_finished,
            ) = (
                self._sprite_renderer
                .draw_yawn(
                    self.t
                )
            )

            if yawn_finished:
                self.state = "idle"


        elif (
            self.state
            in ("idle", "talking")
            and self._sprite_renderer.has_idle
        ):
            top_y = (
                self._sprite_renderer
                .draw_idle(
                    self.t
                )
            )


        else:
            self.cv.delete(
                "all"
            )

            top_y = (
                self.H - 8
            )


        if self.bubble:
            self._bubble_renderer.draw(
                top_y=top_y,
                text=self.bubble,
                mode=self._bubble_mode,
                hover=self._bubble_hover,
            )


        self.root.after(
            self.ANIMATION_TICK_MS,
            self._animate,
        )


    def _handle_bubble_button(
        self,
        button,
    ):
        """
        Executa a acao associada ao botao
        identificado pelo BubbleRenderer.
        """

        if button == "complete":
            self.complete_task()


        elif button == "snooze":
            self._reminder_started_at = None
            self._waiting_reaction_stage = 0
            self._bubble_hover = None

            task = self.reminded_task

            if task:
                SnoozeWindow(
                    self.root,
                    self,
                    task,
                )


        elif button in (
            "5",
            "15",
            "30",
            "60",
        ):
            task = self.reminded_task

            if task:
                from datetime import (
                    datetime,
                    timedelta,
                )

                minutes = int(
                    button
                )

                new_time = (
                    datetime.now()
                    + timedelta(
                        minutes=minutes
                    )
                )

                new_date = (
                    new_time.strftime(
                        "%Y-%m-%d"
                    )
                )

                new_hour = (
                    new_time.strftime(
                        "%H:%M"
                    )
                )

                db_adiar(
                    task[0],
                    new_date,
                    new_hour,
                )

                self._bubble_mode = "normal"
                self._bubble_hover = None

                self._next_reminder()


        elif button == "back":
            self._reminder_started_at = (
                time.monotonic()
            )

            self._waiting_reaction_stage = 0

            self._bubble_mode = "alert"
            self._bubble_hover = None


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

    def _enqueue(self, row):
        tid = row[0]
        rep = row[5]

        # Evita colocar a mesma tarefa duas vezes na fila.
        if (
            self._reminders.queue
            .contains_task_id(tid)
        ):
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
        was_empty = not self._reminders.queue

        self._reminders.queue.append(
            row
        )

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

        # Encerra o monitor de lembretes.
        try:
            self._reminders.stop()
        except Exception:
            pass

        try:
            if self._compact_mode:
                self._compact.save_position()
            else:
                cfg["pos_x"] = self.root.winfo_x()
                cfg["pos_y"] = self.root.winfo_y()
                save_cfg(cfg)
        except Exception:
            pass

        try:
            self._tray.stop()
        except Exception:
            pass

        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()

# =============================================================================
if __name__ == "__main__":
    MarvinCompanion().run()





