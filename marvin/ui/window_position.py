import sys


def position_near(
    window,
    anchor,
    anchor_width=None,
    anchor_height=None,
    gap=12,
):
    """
    Posiciona uma janela ao lado do MARVIN,
    respeitando o monitor em que ele esta.
    """

    window.update_idletasks()
    anchor.update_idletasks()

    ww = window.winfo_width()
    wh = window.winfo_height()

    rx = anchor.winfo_x()
    ry = anchor.winfo_y()

    rw = (
        anchor_width
        if anchor_width is not None
        else anchor.winfo_width()
    )

    rh = (
        anchor_height
        if anchor_height is not None
        else anchor.winfo_height()
    )

    # Fallback: monitor principal
    mon_left = 0
    mon_top = 0
    mon_right = anchor.winfo_screenwidth()
    mon_bottom = anchor.winfo_screenheight()

    # Windows: detecta o monitor onde o MARVIN esta
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            user32 = ctypes.windll.user32

            monitor = user32.MonitorFromWindow(
                anchor.winfo_id(),
                2,
            )

            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(
                MONITORINFO
            )

            if user32.GetMonitorInfoW(
                monitor,
                ctypes.byref(info),
            ):
                mon_left = info.rcWork.left
                mon_top = info.rcWork.top
                mon_right = info.rcWork.right
                mon_bottom = info.rcWork.bottom

        except Exception:
            pass

    # Prefere abrir do lado esquerdo
    if rx - ww - gap >= mon_left:
        px = rx - ww - gap

    # Se nao couber, tenta direita
    elif rx + rw + gap + ww <= mon_right:
        px = rx + rw + gap

    # Se ainda nao couber, prende dentro do monitor
    else:
        px = max(
            mon_left,
            min(
                rx - ww - gap,
                mon_right - ww,
            ),
        )

    # Centraliza verticalmente no MARVIN
    py = ry + (rh - wh) // 2

    py = max(
        mon_top,
        min(
            py,
            mon_bottom - wh,
        ),
    )

    window.geometry(
        f"+{px}+{py}"
    )