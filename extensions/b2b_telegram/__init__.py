import json
import logging
import queue
import sys
import time
from collections import deque
from pathlib import Path

from .alert import B2BAlertWindow
from .monitor import B2BTelegramMonitor
from .parser import extrair_arquivos


logger = logging.getLogger(
    "marvin.extensions.b2b_telegram"
)


CONFIG_FILE = (
    Path.home()
    / ".marvin"
    / "extensions"
    / "b2b_telegram"
    / "config.json"
)


# Um aviso B2B deixa de ocupar a interface
# depois de 24 horas sem confirmacao.
# A notificacao permanece no historico.
ALERT_TTL_SECONDS = 24 * 60 * 60


def _carregar_config():
    if not CONFIG_FILE.exists():
        return None

    try:
        return json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception:
        logger.exception(
            "Erro ao carregar configuracao."
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
        logger.info(
            "Extensao instalada, mas nao configurada."
        )
        return []

    if not config.get(
        "enabled",
        False,
    ):
        logger.info(
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
        logger.warning(
            "Configuracao incompleta."
        )
        return []

    entrada_thread = queue.Queue()
    pendentes = deque()

    estado = {
        "janela": None,
        "aviso_ativo": False,
        "notification_id": None,
        "expires_at": None,
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
        """
        Encerra o aviso visual do B2B.

        Se ja existir um lembrete de tarefa
        pendente, devolve o controle visual
        para esse lembrete.

        Caso contrario, MARVIN volta ao idle.
        """
        try:
            fila = getattr(
                comp,
                "_reminder_queue",
                [],
            )

            if fila:
                tarefa = fila[0]

                try:
                    titulo = tarefa[1]
                except Exception:
                    titulo = "tarefa pendente"

                comp._bubble_mode = "alert"
                comp._bubble_hover = None

                comp.state = "alert"
                comp.b_timer = 0
                comp.bubble = (
                    f"Hora de: {titulo}"
                )

                # Reinicia a contagem da
                # reacao de espera do lembrete.
                if hasattr(
                    comp,
                    "_reminder_started_at",
                ):
                    comp._reminder_started_at = (
                        time.monotonic()
                    )

                if hasattr(
                    comp,
                    "_waiting_reaction_stage",
                ):
                    comp._waiting_reaction_stage = 0

            else:
                comp._bubble_mode = "normal"
                comp._bubble_hover = None

                comp.bubble = ""
                comp.b_timer = 0
                comp.state = "idle"

        except Exception:
            logger.exception(
                "Erro ao limpar aviso."
            )

    def entendi():
        notification_id = estado.get(
            "notification_id"
        )

        if notification_id:
            try:
                comp.notifications.marcar_como_lida(
                    notification_id
                )

            except Exception:
                logger.exception(
                    "Erro ao marcar notificacao como lida."
                )

        estado["janela"] = None
        estado["aviso_ativo"] = False
        estado["notification_id"] = None
        estado["expires_at"] = None

        limpar_balao()

        # A proxima mensagem da fila sera
        # exibida no proximo ciclo.
        comp.root.after(
            100,
            processar_fila,
        )


    def expirar_aviso():
        """
        Remove apenas o aviso ativo da interface.

        A notificacao NAO e marcada como lida
        nem removida do historico.
        """
        janela = estado.get(
            "janela"
        )

        if janela is not None:
            try:
                janela.win.destroy()
            except Exception:
                pass

        estado["janela"] = None
        estado["aviso_ativo"] = False
        estado["notification_id"] = None
        estado["expires_at"] = None

        limpar_balao()

        logger.info(
            "Aviso expirou apos 24 horas. "
            "Historico preservado."
        )


    def mostrar_aviso(
        mensagem,
        notification_id=None,
        expira_em=None,
    ):
        if expira_em is None:
            expira_em = (
                time.time()
                + ALERT_TTL_SECONDS
            )

        estado["notification_id"] = (
            notification_id
        )

        estado["expires_at"] = (
            expira_em
        )

        try:
            comp._show_marvin()

            if (
                comp._compact_enabled
                and comp._compact_mode
            ):
                comp._expand_compact_for_reminder()

        except Exception:
            logger.exception(
                "Erro ao mostrar MARVIN."
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

        except Exception:
            logger.exception(
                "Erro no balao."
            )

        estado["aviso_ativo"] = True

        estado["janela"] = (
            B2BAlertWindow(
                comp,
                mensagem,
                entendi,
            )
        )

        logger.info(
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


        # Verifica se o aviso atualmente
        # exibido completou 24 horas.
        if estado["aviso_ativo"]:
            expira_em = estado.get(
                "expires_at"
            )

            if (
                expira_em is not None
                and time.time() >= expira_em
            ):
                expirar_aviso()


        # Procura a proxima mensagem ainda
        # dentro da janela de 24 horas.
        if not estado["aviso_ativo"]:

            while pendentes:
                (
                    mensagem,
                    notification_id,
                    expira_em,
                ) = pendentes.popleft()


                # A mensagem continua no historico,
                # mas nao deve mais abrir popup.
                if time.time() >= expira_em:
                    logger.info(
                        "Aviso pendente expirado. "
                        "Historico preservado."
                    )

                    continue


                mostrar_aviso(
                    mensagem,
                    notification_id,
                    expira_em,
                )

                break


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

        # A validade visual conta a partir
        # do momento em que a mensagem
        # chega ao MARVIN.
        expira_em = (
            time.time()
            + ALERT_TTL_SECONDS
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

        except Exception:
            logger.exception(
                "Erro ao registrar notificacao."
            )

        entrada_thread.put(
            (
                mensagem,
                notification_id,
                expira_em,
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

    logger.info(
        "Extensao iniciada."
    )

    return [monitor]
