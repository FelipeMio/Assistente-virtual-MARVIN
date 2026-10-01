import queue
import sys
import tkinter as tk

from pathlib import Path

from PIL import Image


try:
    import pystray

except ImportError:
    pystray = None


class TrayController:
    """
    Controla o icone da bandeja do Windows.

    Callbacks do pystray sao encaminhados
    para a thread principal do Tkinter.
    """

    def __init__(
        self,
        root,
        *,
        on_show,
        on_new_task,
        on_home,
        on_toggle_compact,
        compact_enabled,
        on_settings,
        on_exit,
    ):
        self.root = root

        self._on_show = on_show

        self._on_new_task = (
            on_new_task
        )

        self._on_home = on_home

        self._on_toggle_compact = (
            on_toggle_compact
        )

        self._compact_enabled = (
            compact_enabled
        )

        self._on_settings = (
            on_settings
        )

        self._on_exit = (
            on_exit
        )

        self._actions = (
            queue.Queue()
        )

        self._icon = None
        self._loop_started = False
        self._stopped = False


    @property
    def running(self):
        return (
            self._icon is not None
        )


    def dispatch(
        self,
        callback,
    ):
        if self._stopped:
            return

        self._actions.put(
            callback
        )


    def _start_action_loop(self):

        if self._loop_started:
            return

        self._loop_started = True

        try:
            self.root.after(
                100,
                self._process_actions,
            )

        except tk.TclError:
            self._loop_started = False


    def _process_actions(self):

        if self._stopped:
            self._loop_started = False
            return

        try:
            while True:

                callback = (
                    self._actions
                    .get_nowait()
                )

                try:
                    callback()

                except Exception as exc:
                    print(
                        "[MARVIN] Erro em acao "
                        f"da bandeja: {exc}"
                    )

        except queue.Empty:
            pass


        try:
            self.root.after(
                100,
                self._process_actions,
            )

        except tk.TclError:
            self._loop_started = False


    def _image(self):

        base = (
            Path(__file__)
            .resolve()
            .parent
            / "assets"
            / "marvin"
        )


        arquivos = [
            (
                base
                / "compact"
                / "01.png"
            ),
            (
                base
                / "idle"
                / "01.png"
            ),
        ]


        for arquivo in arquivos:

            if not arquivo.exists():
                continue

            try:
                imagem = (
                    Image.open(
                        arquivo
                    )
                    .convert(
                        "RGBA"
                    )
                )

                bbox = (
                    imagem
                    .getchannel("A")
                    .getbbox()
                )

                if bbox:
                    imagem = (
                        imagem.crop(
                            bbox
                        )
                    )

                imagem.thumbnail(
                    (56, 56),
                    Image.Resampling.NEAREST,
                )

                canvas = Image.new(
                    "RGBA",
                    (64, 64),
                    (0, 0, 0, 0),
                )

                x = (
                    64
                    - imagem.width
                ) // 2

                y = (
                    64
                    - imagem.height
                ) // 2

                canvas.paste(
                    imagem,
                    (x, y),
                    imagem,
                )

                return canvas

            except Exception as exc:
                print(
                    "[MARVIN] Erro ao carregar "
                    f"icone: {exc}"
                )


        return None


    def start(self):

        self._stopped = False

        self._start_action_loop()


        if self._icon is not None:
            return


        if pystray is None:
            print(
                "[MARVIN] pystray nao instalado. "
                "Bandeja desativada."
            )

            return


        if sys.platform != "win32":
            return


        imagem = self._image()

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
                    self.dispatch(
                        self._on_show
                    ),
                default=True,
            ),

            pystray.MenuItem(
                "Nova tarefa",
                lambda icon, item:
                    self.dispatch(
                        self._on_new_task
                    ),
            ),

            pystray.MenuItem(
                "Central do MARVIN",
                lambda icon, item:
                    self.dispatch(
                        self._on_home
                    ),
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Modo compacto",
                lambda icon, item:
                    self.dispatch(
                        self._on_toggle_compact
                    ),

                checked=lambda item:
                    bool(
                        self._compact_enabled()
                    ),
            ),

            pystray.MenuItem(
                "Configuracoes",
                lambda icon, item:
                    self.dispatch(
                        self._on_settings
                    ),
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Sair",
                lambda icon, item:
                    self.dispatch(
                        self._on_exit
                    ),
            ),
        )


        self._icon = pystray.Icon(
            "MARVIN",
            imagem,
            "MARVIN",
            menu,
        )


        self._icon.run_detached()


        print(
            "[MARVIN] Icone da bandeja iniciado."
        )


    def update_menu(self):

        icon = self._icon

        if icon is None:
            return

        try:
            icon.update_menu()

        except Exception:
            pass


    def stop(self):

        self._stopped = True

        icon = self._icon
        self._icon = None

        if icon is None:
            return

        try:
            icon.stop()

        except Exception:
            pass
