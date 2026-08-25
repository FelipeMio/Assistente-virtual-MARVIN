import json
import sys
import tkinter as tk
from pathlib import Path

from .monitor import GOEMonitor
from .dashboard import abrir_dashboard


EXTENSION_DIR = Path(__file__).resolve().parent
CONFIG_FILE = EXTENSION_DIR / "config.json"


def _carregar_config():
    if not CONFIG_FILE.exists():
        return None

    try:
        with CONFIG_FILE.open(
            "r",
            encoding="utf-8-sig",
        ) as f:
            return json.load(f)

    except Exception as exc:
        print(
            f"[GOE] Erro ao ler config.json: {exc}"
        )
        return None


def _beep():
    try:
        if sys.platform == "win32":
            import winsound

            winsound.MessageBeep(
                winsound.MB_ICONEXCLAMATION
            )

    except Exception:
        pass


class GOEAlertWindow:

    def __init__(
        self,
        comp,
        status,
    ):
        self.comp = comp

        self.win = tk.Toplevel(comp.root)

        self.win.title(
            "MARVIN - Monitor GOE"
        )

        self.win.attributes(
            "-topmost",
            True,
        )

        self.win.resizable(
            False,
            False,
        )

        self.win.configure(
            bg="#0d1117"
        )

        # O alerta deve ser reconhecido
        # explicitamente pelo botao OK.
        self.win.protocol(
            "WM_DELETE_WINDOW",
            lambda: None,
        )

        self.titulo = tk.Label(
            self.win,
            text="GOE PAROU",
            bg="#0d1117",
            fg="#f85149",
            font=("Consolas", 14, "bold"),
        )

        self.titulo.pack(
            padx=30,
            pady=(22, 8),
        )

        self.mensagem = tk.Label(
            self.win,
            bg="#0d1117",
            fg="#e6edf3",
            font=("Consolas", 10),
            justify="center",
            wraplength=300,
        )

        self.mensagem.pack(
            padx=25,
            pady=(0, 18),
        )

        self.botao = tk.Button(
            self.win,
            text="OK",
            bg="#3fb950",
            fg="#0d1117",
            bd=0,
            padx=35,
            pady=8,
            font=("Consolas", 10, "bold"),
            cursor="hand2",
            command=self.fechar,
        )

        self.botao.pack(
            pady=(0, 22)
        )

        self.mostrar_parado(status)
        self._posicionar()


    def _posicionar(self):
        self.win.update_idletasks()

        largura = self.win.winfo_reqwidth()
        altura = self.win.winfo_reqheight()

        try:
            x = (
                self.comp.root.winfo_x()
                - largura
                - 15
            )

            y = self.comp.root.winfo_y()

        except Exception:
            x = 100
            y = 100

        self.win.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        self.win.lift()


    def mostrar_parado(
        self,
        status,
    ):
        hora = int(
            status.get("hora", 0)
        )

        self.titulo.config(
            text="GOE PAROU",
            fg="#f85149",
        )

        self.mensagem.config(
            text=(
                f"A hora das {hora:02d}h "
                "retornou 0 registros.\n\n"
                "Verifique o monitoramento."
            )
        )

        self.win.lift()


    def mostrar_voltou(
        self,
        status,
    ):
        hora = int(
            status.get("hora", 0)
        )

        qtde = int(
            status.get("qtde", 0)
        )

        self.titulo.config(
            text="GOE VOLTOU",
            fg="#3fb950",
        )

        self.mensagem.config(
            text=(
                "O GOE voltou ao normal.\n\n"
                f"{hora:02d}h: "
                f"{qtde} registros."
            )
        )

        self.win.lift()


    def fechar(self):
        try:
            self.win.destroy()
        except Exception:
            pass

        if not self.comp._reminder_queue:
            self.comp.bubble = ""
            self.comp.b_timer = 0
            self.comp.state = "idle"


def iniciar_extensao(comp):
    config = _carregar_config()

    # Sem config.json:
    # extensao instalada, mas desligada.
    if not config:
        print(
            "[GOE] Extensao instalada, "
            "mas nao configurada."
        )
        return []

    if not config.get(
        "enabled",
        False,
    ):
        print(
            "[GOE] Monitor desativado."
        )
        return []

    arquivo = config.get(
        "csv_path"
    )

    avisar_ok = config.get(
        "notify_ok",
        True,
    )

    avisar_parado = config.get(
        "notify_stopped",
        True,
    )

    som = config.get(
        "sound",
        True,
    )

    estado = {
        "janela_alerta": None,
    }


    def mostrar_marvin():
        comp._show_marvin()

        if (
            comp._compact_enabled
            and comp._compact_mode
        ):
            comp._expand_compact_for_reminder()


    def goe_parou(status):
        if not avisar_parado:
            return

        if comp._reminder_queue:
            comp.root.after(
                5000,
                lambda s=dict(status):
                    goe_parou(s),
            )
            return

        if not monitor.em_alerta:
            return

        mostrar_marvin()

        comp._bubble_mode = "normal"
        comp._bubble_hover = None

        if som:
            _beep()

        hora = int(
            status.get("hora", 0)
        )

        comp.say(
            (
                "Ei, o GOE parou! "
                f"A hora das {hora:02d}h "
                "retornou 0."
            ),
            "alert",
            86400000,
        )

        janela = estado.get(
            "janela_alerta"
        )

        if (
            janela is not None
            and janela.win.winfo_exists()
        ):
            janela.mostrar_parado(
                status
            )

        else:
            estado["janela_alerta"] = (
                GOEAlertWindow(
                    comp,
                    status,
                )
            )


    def goe_voltou(status):
        mostrar_marvin()

        janela = estado.get(
            "janela_alerta"
        )

        if (
            janela is not None
            and janela.win.winfo_exists()
        ):
            janela.mostrar_voltou(
                status
            )

        hora = int(
            status.get("hora", 0)
        )

        qtde = int(
            status.get("qtde", 0)
        )

        comp.say(
            (
                "GOE voltou ao normal! "
                f"{hora:02d}h teve "
                f"{qtde} registros."
            ),
            "talking",
            8000,
        )


    def goe_ok(status):
        if not avisar_ok:
            return

        if comp._reminder_queue:
            comp.root.after(
                5000,
                lambda s=dict(status):
                    goe_ok(s),
            )
            return

        mostrar_marvin()

        hora = int(
            status.get("hora", 0)
        )

        qtde = int(
            status.get("qtde", 0)
        )

        comp.say(
            (
                "Por enquanto, GOE tudo certo! "
                f"{hora:02d}h: "
                f"{qtde} registros."
            ),
            "talking",
            7000,
        )


    monitor = GOEMonitor(
        comp.root,
        on_parou=goe_parou,
        on_voltou=goe_voltou,
        on_ok=goe_ok,
        arquivo=arquivo,
    )

    monitor.start()

    # Registra a interface publica da extensao
    # para a Central do MARVIN.
    if not hasattr(
        comp,
        "_extension_actions",
    ):
        comp._extension_actions = {}

    comp._extension_actions[
        "GOE hora a hora"
    ] = lambda: abrir_dashboard(
        comp.root,
        comp,
    )

    print(
        "[GOE] Monitor iniciado."
    )

    return [monitor]

