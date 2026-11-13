"""
Atalho de teclado global (funciona com qualquer janela em foco).

No Windows o atalho e registrado com RegisterHotKey numa thread
propria, que fica num laco de mensagens. Quando o atalho e
pressionado, o pedido vai para uma fila e e executado na thread
do Tkinter (o Tk nao pode ser usado fora da thread principal).
"""

import logging
import queue
import sys
import threading
import tkinter as tk


logger = logging.getLogger(
    "marvin.hotkey"
)


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

_MODIFICADORES = {
    "ctrl": MOD_CONTROL,
    "control": MOD_CONTROL,
    "alt": MOD_ALT,
    "shift": MOD_SHIFT,
    "win": MOD_WIN,
}


def parse_atalho(texto):
    """
    "Ctrl+Alt+M" -> (modificadores, virtual_key).

    Aceita letras, numeros e F1..F12. Devolve None se invalido.
    """
    partes = [
        p.strip().lower()
        for p in str(texto).split("+")
        if p.strip()
    ]

    if len(partes) < 2:
        return None

    mods = 0

    for parte in partes[:-1]:
        if parte not in _MODIFICADORES:
            return None
        mods |= _MODIFICADORES[parte]

    tecla = partes[-1]

    if len(tecla) == 1 and tecla.isalnum():
        vk = ord(tecla.upper())

    elif tecla.startswith("f") and tecla[1:].isdigit() and 1 <= int(tecla[1:]) <= 12:
        vk = 0x70 + int(tecla[1:]) - 1

    elif tecla == "space":
        vk = 0x20

    else:
        return None

    return mods, vk


class GlobalHotkey:

    HOTKEY_ID = 0x4D41  # "MA"

    def __init__(
        self,
        root,
        atalho,
        callback,
    ):
        self.root = root
        self.atalho = atalho
        self._callback = callback

        self._fila = queue.Queue()
        self._thread = None
        self._thread_id = None
        self._job = None
        self._parado = False

        self.registrado = False

    # ========================================================
    # CICLO DE VIDA
    # ========================================================

    def start(self):
        if sys.platform != "win32":
            logger.info("Atalho global so existe no Windows.")
            return

        combinacao = parse_atalho(self.atalho)

        if combinacao is None:
            logger.warning("Atalho invalido: %s", self.atalho)
            return

        self._parado = False

        self._thread = threading.Thread(
            target=self._loop,
            args=combinacao,
            daemon=True,
            name="marvin-hotkey",
        )
        self._thread.start()

        self._agendar()

    def stop(self):
        self._parado = True

        if self._job is not None:
            try:
                self.root.after_cancel(self._job)
            except Exception:
                pass

            self._job = None

        if self._thread_id is not None:
            try:
                import ctypes

                ctypes.windll.user32.PostThreadMessageW(
                    self._thread_id,
                    WM_QUIT,
                    0,
                    0,
                )
            except Exception:
                logger.exception("Erro ao encerrar o atalho.")

        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._thread is not threading.current_thread()
        ):
            self._thread.join(timeout=1.0)

        self._thread = None
        self._thread_id = None

    # ========================================================
    # THREAD DO WINDOWS
    # ========================================================

    def _loop(self, mods, vk):
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        self._thread_id = kernel32.GetCurrentThreadId()

        if not user32.RegisterHotKey(
            None,
            self.HOTKEY_ID,
            mods | MOD_NOREPEAT,
            vk,
        ):
            logger.warning(
                "Nao foi possivel registrar %s "
                "(talvez outro programa ja use esse atalho).",
                self.atalho,
            )
            return

        self.registrado = True
        logger.info("Atalho global %s registrado.", self.atalho)

        msg = wintypes.MSG()

        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if (
                    msg.message == WM_HOTKEY
                    and msg.wParam == self.HOTKEY_ID
                ):
                    self._fila.put(True)

        finally:
            user32.UnregisterHotKey(None, self.HOTKEY_ID)
            self.registrado = False

    # ========================================================
    # THREAD DO TK
    # ========================================================

    def _agendar(self):
        if self._parado:
            return

        try:
            self._job = self.root.after(80, self._processar)
        except tk.TclError:
            self._job = None

    def _processar(self):
        self._job = None

        disparou = False

        try:
            while True:
                self._fila.get_nowait()
                disparou = True
        except queue.Empty:
            pass

        if disparou:
            try:
                self._callback()
            except Exception:
                logger.exception("Erro ao executar o atalho.")

        self._agendar()
