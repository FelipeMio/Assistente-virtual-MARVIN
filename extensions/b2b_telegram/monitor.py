import json
import threading
import urllib.parse
import urllib.request


class B2BTelegramMonitor:

    def __init__(
        self,
        token,
        chat_id,
        sender_username,
        message_prefix,
        on_message=None,
    ):
        self.token = token
        self.chat_id = str(chat_id)
        self.sender_username = sender_username
        self.message_prefix = message_prefix
        self.on_message = on_message

        self._stop_event = threading.Event()
        self._thread = None
        self._offset = None

    def _api_url(self):
        return (
            f"https://api.telegram.org/"
            f"bot{self.token}/getUpdates"
        )

    def _get_updates(
        self,
        offset=None,
        timeout=0,
        limit=100,
    ):
        dados = {
            "timeout": timeout,
            "limit": limit,
            "allowed_updates": json.dumps(
                ["message"]
            ),
        }

        if offset is not None:
            dados["offset"] = offset

        url = (
            self._api_url()
            + "?"
            + urllib.parse.urlencode(dados)
        )

        with urllib.request.urlopen(
            url,
            timeout=timeout + 10,
        ) as resposta:
            payload = json.loads(
                resposta.read().decode("utf-8")
            )

        if not payload.get("ok"):
            raise RuntimeError(
                "Telegram retornou ok=False"
            )

        return payload.get("result", [])

    def _mensagem_valida(self, update):
        mensagem = update.get("message")

        if not mensagem:
            return None

        chat = mensagem.get("chat", {})
        remetente = mensagem.get("from", {})
        texto = mensagem.get("text")

        if str(chat.get("id")) != self.chat_id:
            return None

        if remetente.get("is_bot") is not True:
            return None

        if (
            remetente.get("username")
            != self.sender_username
        ):
            return None

        if not isinstance(texto, str):
            return None

        if (
            self.message_prefix
            and self.message_prefix not in texto
        ):
            return None

        return texto

    def _definir_ponto_inicial(self):
        """
        Ignora mensagens que ja existiam
        antes do monitor ser iniciado.
        """
        updates = self._get_updates(
            timeout=0,
            limit=100,
        )

        if updates:
            ultimo_id = max(
                int(update["update_id"])
                for update in updates
            )

            self._offset = ultimo_id + 1

        else:
            self._offset = None

    def _run(self):
        try:
            self._definir_ponto_inicial()

            print(
                "[B2B Telegram] "
                "Monitor conectado."
            )

        except Exception as exc:
            print(
                "[B2B Telegram] "
                "Falha ao iniciar: "
                f"{exc}"
            )

            self._offset = None

        while not self._stop_event.is_set():

            try:
                updates = self._get_updates(
                    offset=self._offset,
                    timeout=20,
                )

            except Exception as exc:
                if self._stop_event.is_set():
                    break

                print(
                    "[B2B Telegram] "
                    "Erro ao consultar Telegram: "
                    f"{exc}"
                )

                self._stop_event.wait(5)
                continue

            for update in updates:

                try:
                    update_id = int(
                        update["update_id"]
                    )

                    self._offset = update_id + 1

                    texto = self._mensagem_valida(
                        update
                    )

                    if texto is None:
                        continue

                    print(
                        "[B2B Telegram] "
                        "Aviso valido recebido."
                    )

                    if self.on_message:
                        self.on_message(texto)

                except Exception as exc:
                    print(
                        "[B2B Telegram] "
                        "Erro ao processar update: "
                        f"{exc}"
                    )

    def start(self):
        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="B2BTelegramMonitor",
        )

        self._thread.start()

    def stop(self):
        self._stop_event.set()

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            self._thread.join(
                timeout=2
            )
