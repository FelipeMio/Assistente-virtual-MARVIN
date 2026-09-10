import json
import queue
import sys
from collections import deque
from pathlib import Path

from .alert import B2BAlertWindow
from .monitor import B2BTelegramMonitor
from .parser import extrair_arquivos


CONFIG_FILE = (
    Path.home()
    / ".marvin"
    / "extensions"
    / "b2b_telegram"
    / "config.json"
)


def _carregar_config():
    if not CONFIG_FILE.exists():
        return None

    try:
        return json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception as exc:
        print(
            "[B2B Telegram] "
            f"Erro ao carregar configuracao: {exc}"
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


def iniciar_extensao(comp):
    config = _carregar_config()

    if not config:
        print(
            "[B2B Telegram] "
            "Extensao instalada, mas nao configurada."
        )
        return []

    if not config.get(
        "enabled",
        False,
    ):
        print(
            "[B2B Telegram] "
            "Monitor desativado."
        )
        return []

    token = config.get("token")
    chat_id = config.get("chat_id")
    sender_username = config.get(
        "sender_username"
    )

    # Vazio = aceita qualquer mensagem
    # enviada pelo robo configurado.
    message_prefix = config.get(
        "message_prefix",
        "",
    )

    if not all(
        [
            token,
            chat_id,
            sender_username,
        ]
    ):
        print(
            "[B2B Telegram] "
            "Configuracao incompleta."
        )
        return []

    entrada_thread = queue.Queue()
    pendentes = deque()

    estado = {
        "janela": None,
        "aviso_ativo": False,
        "notification_id": None,
    }

    def preparar_mensagem(texto):
        arquivos = extrair_arquivos(texto)

        if arquivos:
            if len(arquivos) == 1:
                item = arquivos[0]

                return (
                    "Chegou um novo arquivo no B2B.\n\n"
                    f"Arquivo:\n{item['arquivo']}\n\n"
                    f"Pasta:\n{item['pasta']}"
                )

            linhas = [
                f"{len(arquivos)} novos arquivos "
                "chegaram no B2B.\n"
            ]

            for item in arquivos:
                linhas.append(
                    f"• {item['arquivo']}"
                )

            return "\n".join(linhas)

        # Para qualquer outro tipo de mensagem
        # enviada pelo robo.
        texto_limpo = texto.strip()

        if len(texto_limpo) > 700:
            texto_limpo = (
                texto_limpo[:697]
                + "..."
            )

        return (
            "Nova mensagem recebida no B2B:\n\n"
            + texto_limpo
        )

    def limpar_balao():
        try:
            if not comp._reminder_queue:
                comp.bubble = ""
                comp.b_timer = 0
                comp.state = "idle"
        except Exception:
            pass

    def entendi():
        notification_id = estado.get(
            "notification_id"
        )

        if notification_id:
            try:
                comp.notifications.marcar_como_lida(
                    notification_id
                )

            except Exception as exc:
                print(
                    "[B2B Telegram] "
                    "Erro ao marcar notificacao "
                    f"como lida: {exc}"
                )

        estado["janela"] = None
        estado["aviso_ativo"] = False
        estado["notification_id"] = None

        limpar_balao()

        # A proxima mensagem da fila sera
        # exibida no proximo ciclo.
        comp.root.after(
            100,
            processar_fila,
        )

    def mostrar_aviso(
        mensagem,
        notification_id=None,
    ):
        estado["notification_id"] = (
            notification_id
        )

        try:
            comp._show_marvin()

            if (
                comp._compact_enabled
                and comp._compact_mode
            ):
                comp._expand_compact_for_reminder()

        except Exception as exc:
            print(
                "[B2B Telegram] "
                f"Erro ao mostrar MARVIN: {exc}"
            )

        _beep()

        try:
            comp._bubble_mode = "normal"
            comp._bubble_hover = None

            comp.say(
                "Novo aviso do B2B. "
                "Confirme quando visualizar.",
                "alert",
                2000000000,
            )

        except Exception as exc:
            print(
                "[B2B Telegram] "
                f"Erro no balao: {exc}"
            )

        estado["aviso_ativo"] = True

        estado["janela"] = (
            B2BAlertWindow(
                comp,
                mensagem,
                entendi,
            )
        )

        print(
            "[B2B Telegram] "
            "Aviso exibido no MARVIN."
        )

    def processar_fila():
        try:
            while True:
                pendentes.append(
                    entrada_thread.get_nowait()
                )

        except queue.Empty:
            pass

        if (
            not estado["aviso_ativo"]
            and pendentes
        ):
            mensagem, notification_id = (
                pendentes.popleft()
            )

            mostrar_aviso(
                mensagem,
                notification_id,
            )

        try:
            comp.root.after(
                250,
                processar_fila,
            )

        except Exception:
            pass

    def recebeu_mensagem(texto):
        # Esta funcao roda na thread
        # do Telegram.

        mensagem = preparar_mensagem(
            texto
        )

        notification_id = None

        try:
            notification_id = (
                comp.notifications.adicionar(
                    origem="B2B",
                    titulo="Novo aviso B2B",
                    mensagem=mensagem,
                    metadata={
                        "extensao": "b2b_telegram",
                    },
                )
            )

        except Exception as exc:
            print(
                "[B2B Telegram] "
                "Erro ao registrar notificacao: "
                f"{exc}"
            )

        entrada_thread.put(
            (
                mensagem,
                notification_id,
            )
        )

    monitor = B2BTelegramMonitor(
        token=token,
        chat_id=chat_id,
        sender_username=sender_username,
        message_prefix=message_prefix,
        on_message=recebeu_mensagem,
    )

    # Inicia o consumidor da fila dentro
    # da thread principal do Tkinter.
    comp.root.after(
        250,
        processar_fila,
    )

    monitor.start()

    print(
        "[B2B Telegram] "
        "Extensao iniciada."
    )

    return [monitor]
