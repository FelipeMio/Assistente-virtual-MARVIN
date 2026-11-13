"""
Trazer uma janela do MARVIN para a frente COM o foco do teclado.

O Windows impede que um programa em segundo plano "roube" o foco
de quem o usuario esta usando. Por isso, sem este cuidado, a janela
aberta pelo atalho global aparecia, mas o que se digitava continuava
indo para o outro programa (so funcionava depois de clicar no gato).
"""

import logging
import sys


logger = logging.getLogger(
    "marvin.focus"
)

GA_ROOT = 2
SW_SHOW = 5
VK_MENU = 0x12
KEYEVENTF_KEYUP = 0x0002


def _hwnd(win):
    import ctypes

    user32 = ctypes.windll.user32
    hwnd = user32.GetAncestor(win.winfo_id(), GA_ROOT)
    return hwnd or win.winfo_id()


def _ativar(hwnd):
    import ctypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    frente = user32.GetForegroundWindow()
    thread_frente = user32.GetWindowThreadProcessId(frente, None)
    thread_atual = kernel32.GetCurrentThreadId()

    ligado = False

    # Compartilhar a fila de entrada com o programa da frente
    # permite que o Windows aceite a troca de foco.
    if thread_frente and thread_frente != thread_atual:
        ligado = bool(
            user32.AttachThreadInput(thread_frente, thread_atual, True)
        )

    try:
        user32.ShowWindow(hwnd, SW_SHOW)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SetActiveWindow(hwnd)
        user32.SetFocus(hwnd)

    finally:
        if ligado:
            user32.AttachThreadInput(thread_frente, thread_atual, False)

    return user32.GetForegroundWindow() == hwnd


def trazer_para_frente(win, entrada=None):
    """
    Mostra `win` na frente e coloca o cursor em `entrada`.
    Devolve True se a janela ficou com o foco.
    """
    try:
        win.deiconify()
        win.lift()
        win.attributes("-topmost", True)
        win.update_idletasks()
    except Exception:
        return False

    conseguiu = True

    if sys.platform == "win32":
        try:
            import ctypes

            hwnd = _hwnd(win)
            conseguiu = _ativar(hwnd)

            if not conseguiu:
                # Ultimo recurso: um "toque" na tecla Alt faz o
                # Windows considerar o MARVIN o dono da ultima
                # entrada do teclado e liberar a troca de foco.
                user32 = ctypes.windll.user32
                user32.keybd_event(VK_MENU, 0, 0, 0)
                user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
                conseguiu = _ativar(hwnd)

        except Exception:
            logger.exception("Erro ao trazer janela para a frente.")
            conseguiu = False

    try:
        win.focus_force()

        if entrada is not None:
            entrada.focus_set()
    except Exception:
        pass

    if not conseguiu:
        logger.warning("O Windows nao liberou o foco para a janela.")

    return conseguiu
