import copy
import json
import threading

from datetime import datetime
from pathlib import Path
from uuid import uuid4


DEFAULT_HISTORY_LIMIT = 200


class NotificationManager:

    def __init__(
        self,
        storage_file=None,
        history_limit=DEFAULT_HISTORY_LIMIT,
    ):
        if storage_file is None:
            storage_file = (
                Path.home()
                / ".marvin"
                / "notifications.json"
            )

        self.storage_file = Path(storage_file)
        self.history_limit = max(
            1,
            int(history_limit),
        )

        self._lock = threading.RLock()
        self._items = []

        self._load()

    def _load(self):
        if not self.storage_file.exists():
            return

        try:
            dados = json.loads(
                self.storage_file.read_text(
                    encoding="utf-8-sig"
                )
            )

            if not isinstance(dados, list):
                return

            self._items = [
                item
                for item in dados
                if isinstance(item, dict)
                and item.get("id")
            ][:self.history_limit]

        except Exception as exc:
            print(
                "[MARVIN Notifications] "
                f"Erro ao carregar historico: {exc}"
            )

    def _save_locked(self):
        try:
            self.storage_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            temp_file = (
                self.storage_file.parent
                / (
                    self.storage_file.name
                    + ".tmp"
                )
            )

            temp_file.write_text(
                json.dumps(
                    self._items,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            temp_file.replace(
                self.storage_file
            )

        except Exception as exc:
            print(
                "[MARVIN Notifications] "
                f"Erro ao salvar historico: {exc}"
            )

    def adicionar(
        self,
        origem,
        titulo,
        mensagem,
        metadata=None,
    ):
        item = {
            "id": str(uuid4()),
            "origem": str(origem),
            "titulo": str(titulo),
            "mensagem": str(mensagem),
            "criada_em": (
                datetime.now()
                .astimezone()
                .isoformat(timespec="seconds")
            ),
            "lida": False,
            "metadata": (
                metadata
                if isinstance(metadata, dict)
                else {}
            ),
        }

        with self._lock:
            self._items.insert(0, item)

            del self._items[
                self.history_limit:
            ]

            self._save_locked()

        return item["id"]

    def listar(
        self,
        limite=None,
        somente_nao_lidas=False,
    ):
        with self._lock:
            itens = copy.deepcopy(
                self._items
            )

        if somente_nao_lidas:
            itens = [
                item
                for item in itens
                if not item.get("lida", False)
            ]

        if limite is not None:
            itens = itens[
                :max(0, int(limite))
            ]

        return itens

    def quantidade_nao_lidas(self):
        with self._lock:
            return sum(
                1
                for item in self._items
                if not item.get("lida", False)
            )

    def marcar_como_lida(
        self,
        notification_id,
    ):
        alterou = False

        with self._lock:
            for item in self._items:
                if (
                    item.get("id")
                    == notification_id
                ):
                    if not item.get(
                        "lida",
                        False,
                    ):
                        item["lida"] = True
                        alterou = True

                    break

            if alterou:
                self._save_locked()

        return alterou

    def marcar_todas_como_lidas(self):
        alterou = False

        with self._lock:
            for item in self._items:
                if not item.get(
                    "lida",
                    False,
                ):
                    item["lida"] = True
                    alterou = True

            if alterou:
                self._save_locked()

        return alterou

    def limpar(self):
        with self._lock:
            self._items.clear()
            self._save_locked()
