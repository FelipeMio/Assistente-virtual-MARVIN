import sys
import tkinter as tk


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


class CompactModeController:

    def __init__(
        self,
        root,
        canvas,
        *,
        config,
        save_config,
        normal_size,
        compact_size,
        on_drag_distance=None,
    ):
        self.root = root
        self.canvas = canvas

        self.config = config
        self._save_config = save_config

        self.normal_width = int(normal_size[0])
        self.normal_height = int(normal_size[1])

        self.compact_width = int(compact_size[0])
        self.compact_height = int(compact_size[1])

        self._on_drag_distance = on_drag_distance

        self.enabled = False
        self.mode = False

        self._normal_position = None
        self._has_position = False

        self._drag_active = False
        self._drag_job = None
        self._drag_offset_x = 0
        self._drag_start = None
        self._drag_distance = 0


    # ========================================================
    # WIN32
    # ========================================================

    def _root_hwnd(self):
        if sys.platform != "win32":
            return None

        try:
            user32 = ctypes.windll.user32

            user32.GetAncestor.argtypes = [
                wintypes.HWND,
                wintypes.UINT,
            ]

            user32.GetAncestor.restype = wintypes.HWND

            hwnd = self.root.winfo_id()

            root_hwnd = user32.GetAncestor(
                hwnd,
                2,
            )

            return root_hwnd or hwnd

        except Exception as exc:
            print(
                "[MARVIN] Erro ao obter HWND: "
                f"{exc}"
            )
            return None


    def _cursor_position(self):
        if sys.platform == "win32":
            try:
                point = wintypes.POINT()

                if ctypes.windll.user32.GetCursorPos(
                    ctypes.byref(point)
                ):
                    return (
                        point.x,
                        point.y,
                    )

            except Exception:
                pass

        return (
            self.root.winfo_pointerx(),
            self.root.winfo_pointery(),
        )


    def _workarea_from_point(
        self,
        x,
        y,
    ):
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32

                user32.MonitorFromPoint.argtypes = [
                    wintypes.POINT,
                    wintypes.DWORD,
                ]

                user32.MonitorFromPoint.restype = (
                    ctypes.c_void_p
                )

                user32.GetMonitorInfoW.argtypes = [
                    ctypes.c_void_p,
                    ctypes.POINTER(MONITORINFO),
                ]

                user32.GetMonitorInfoW.restype = (
                    wintypes.BOOL
                )

                point = wintypes.POINT(
                    int(x),
                    int(y),
                )

                monitor = user32.MonitorFromPoint(
                    point,
                    2,
                )

                info = MONITORINFO()

                info.cbSize = ctypes.sizeof(
                    MONITORINFO
                )

                if (
                    monitor
                    and user32.GetMonitorInfoW(
                        monitor,
                        ctypes.byref(info),
                    )
                ):
                    return (
                        info.rcWork.left,
                        info.rcWork.top,
                        info.rcWork.right,
                        info.rcWork.bottom,
                    )

            except Exception as exc:
                print(
                    "[MARVIN] Erro ao detectar "
                    f"monitor: {exc}"
                )

        return (
            0,
            0,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
        )


    def _window_rect(self):
        hwnd = self._root_hwnd()

        if hwnd is not None:
            try:
                rect = wintypes.RECT()

                if ctypes.windll.user32.GetWindowRect(
                    hwnd,
                    ctypes.byref(rect),
                ):
                    return (
                        rect.left,
                        rect.top,
                        rect.right,
                        rect.bottom,
                    )

            except Exception:
                pass

        x = self.root.winfo_x()
        y = self.root.winfo_y()

        return (
            x,
            y,
            x + self.root.winfo_width(),
            y + self.root.winfo_height(),
        )


    def _move_resize(
        self,
        x,
        y,
        width,
        height,
    ):
        hwnd = self._root_hwnd()

        if (
            sys.platform == "win32"
            and hwnd is not None
        ):
            try:
                user32 = ctypes.windll.user32

                user32.SetWindowPos.argtypes = [
                    wintypes.HWND,
                    wintypes.HWND,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    wintypes.UINT,
                ]

                user32.SetWindowPos.restype = (
                    wintypes.BOOL
                )

                ok = user32.SetWindowPos(
                    hwnd,
                    None,
                    int(x),
                    int(y),
                    int(width),
                    int(height),
                    0x0004
                    | 0x0010
                    | 0x0040,
                )

                if ok:
                    return True

            except Exception as exc:
                print(
                    "[MARVIN] Erro ao mover "
                    f"janela: {exc}"
                )

        return False


    # ========================================================
    # POSITION
    # ========================================================

    def set_normal_position(
        self,
        x,
        y,
    ):
        self._normal_position = (
            int(x),
            int(y),
        )


    def save_position(self):
        left, top, right, bottom = (
            self._window_rect()
        )

        self.config["pos_compact_x"] = int(left)
        self.config["pos_compact_y"] = int(top)

        self._has_position = True

        self._save_config(
            self.config
        )


    # ========================================================
    # LAYOUT
    # ========================================================

    def enter(
        self,
        remember_normal=False,
    ):
        if remember_normal:
            rect = self._window_rect()

            self._normal_position = (
                rect[0],
                rect[1],
            )

            self.config["pos_x"] = rect[0]
            self.config["pos_y"] = rect[1]


        if self._has_position:
            compact_x = self.config.get(
                "pos_compact_x"
            )

            compact_y = self.config.get(
                "pos_compact_y"
            )

        else:
            rect = self._window_rect()

            compact_x = rect[0]
            compact_y = rect[1]


        if not isinstance(compact_x, int):
            compact_x = self.root.winfo_x()

        if not isinstance(compact_y, int):
            compact_y = self.root.winfo_y()


        left, top, right, bottom = (
            self._workarea_from_point(
                compact_x
                + self.compact_width // 2,
                compact_y,
            )
        )


        compact_x = max(
            left,
            min(
                compact_x,
                right - self.compact_width,
            ),
        )

        compact_y = (
            bottom - self.compact_height
        )


        self.mode = True


        self.canvas.config(
            width=self.compact_width,
            height=self.compact_height,
        )


        self._move_resize(
            compact_x,
            compact_y,
            self.compact_width,
            self.compact_height,
        )


        self.config["pos_compact_x"] = compact_x
        self.config["pos_compact_y"] = compact_y

        self._has_position = True

        self._save_config(
            self.config
        )


    def restore(self):
        self.finish_drag()

        self.mode = False

        self.canvas.config(
            width=self.normal_width,
            height=self.normal_height,
        )


        pos = self._normal_position


        if pos is None:
            px = self.config.get("pos_x")
            py = self.config.get("pos_y")

            if (
                isinstance(px, int)
                and isinstance(py, int)
            ):
                pos = (
                    px,
                    py,
                )


        if pos is None:
            pos = (
                self.root.winfo_x(),
                self.root.winfo_y(),
            )


        self._move_resize(
            pos[0],
            pos[1],
            self.normal_width,
            self.normal_height,
        )


    def expand_for_reminder(self):
        rect = self._window_rect()

        compact_x = rect[0]
        compact_y = rect[1]


        self.config["pos_compact_x"] = compact_x
        self.config["pos_compact_y"] = compact_y

        self._has_position = True

        self.finish_drag()

        self.mode = False


        left, top, right, bottom = (
            self._workarea_from_point(
                compact_x
                + self.compact_width // 2,
                compact_y
                + self.compact_height // 2,
            )
        )


        x = max(
            left,
            min(
                compact_x,
                right - self.normal_width,
            ),
        )

        y = max(
            top,
            bottom - self.normal_height,
        )


        self.canvas.config(
            width=self.normal_width,
            height=self.normal_height,
        )


        self._move_resize(
            x,
            y,
            self.normal_width,
            self.normal_height,
        )


        self._save_config(
            self.config
        )


    # ========================================================
    # DRAG
    # ========================================================

    def begin_drag(self):
        if not self.mode:
            return

        if self._drag_active:
            self.finish_drag()

        mouse_x, mouse_y = (
            self._cursor_position()
        )

        rect = self._window_rect()

        self._drag_offset_x = (
            mouse_x - rect[0]
        )

        self._drag_start = (
            mouse_x,
            mouse_y,
        )

        self._drag_distance = 0
        self._drag_active = True

        self._drag_tick()


    def finish_drag(self):
        distance = self._drag_distance
        was_active = self._drag_active

        self._drag_active = False
        self._drag_start = None

        if self._drag_job is not None:
            try:
                self.root.after_cancel(
                    self._drag_job
                )
            except Exception:
                pass

            self._drag_job = None


        if was_active:
            self.save_position()


        return distance


    def _report_drag_distance(
        self,
        distance,
    ):
        callback = self._on_drag_distance

        if callback is None:
            return

        try:
            callback(distance)

        except Exception:
            pass


    def _drag_tick(self):
        if self._drag_job is not None:
            try:
                self.root.after_cancel(
                    self._drag_job
                )
            except Exception:
                pass

            self._drag_job = None


        if (
            not self._drag_active
            or not self.mode
        ):
            return


        if sys.platform == "win32":
            try:
                pressed = (
                    ctypes.windll.user32
                    .GetAsyncKeyState(0x01)
                    & 0x8000
                )

                if not pressed:
                    self.finish_drag()
                    return

            except Exception:
                pass


        mouse_x, mouse_y = (
            self._cursor_position()
        )


        if self._drag_start:
            sx, sy = self._drag_start

            dist = (
                abs(mouse_x - sx)
                + abs(mouse_y - sy)
            )

            self._drag_distance = max(
                self._drag_distance,
                dist,
            )

            if self._drag_distance > 4:
                self._report_drag_distance(
                    self._drag_distance
                )


        left, top, right, bottom = (
            self._workarea_from_point(
                mouse_x,
                mouse_y,
            )
        )


        x = (
            mouse_x
            - self._drag_offset_x
        )

        x = max(
            left,
            min(
                x,
                right - self.compact_width,
            ),
        )

        y = (
            bottom - self.compact_height
        )


        self._move_resize(
            x,
            y,
            self.compact_width,
            self.compact_height,
        )


        try:
            self._drag_job = (
                self.root.after(
                    16,
                    self._drag_tick,
                )
            )

        except tk.TclError:
            self._drag_job = None
            self._drag_active = False
