class MouseInteractionController:
    """
    Controla drag, hover e eventos de mouse
    do personagem principal.
    """

    def __init__(
        self,
        root,
        canvas,
        *,
        config,
        save_config,
        compact,
        compact_mode,
        bubble_button_at,
        get_hover,
        set_hover,
        on_button,
        on_right_click,
        drag_threshold=4,
    ):
        self.root = root
        self.canvas = canvas

        self.config = config
        self._save_config = save_config

        self.compact = compact

        self._compact_mode = (
            compact_mode
        )

        self._bubble_button_at = (
            bubble_button_at
        )

        self._get_hover = (
            get_hover
        )

        self._set_hover = (
            set_hover
        )

        self._on_button = (
            on_button
        )

        self._on_right_click = (
            on_right_click
        )

        self.drag_threshold = int(
            drag_threshold
        )

        self._dragging = False
        self._drag_distance = 0

        self._dx = 0
        self._dy = 0


    # ========================================================
    # BINDINGS
    # ========================================================

    def bind(self):
        self.canvas.bind(
            "<ButtonPress-1>",
            self.begin_drag,
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.drag,
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.end_drag,
        )

        self.canvas.bind(
            "<Motion>",
            self.mouse_motion,
        )

        self.canvas.bind(
            "<Leave>",
            self.mouse_leave,
        )

        if self._on_right_click is not None:
            self.canvas.bind(
                "<Button-3>",
                self._on_right_click,
            )


    # ========================================================
    # STATE
    # ========================================================

    @property
    def dragging(self):
        return self._dragging


    @property
    def drag_distance(self):
        return self._drag_distance


    def _update_drag_distance(
        self,
        distance,
    ):
        self._drag_distance = max(
            self._drag_distance,
            int(distance),
        )

        if (
            self._drag_distance
            > self.drag_threshold
        ):
            self._dragging = True


    def report_compact_drag_distance(
        self,
        distance,
    ):
        self._update_drag_distance(
            distance
        )


    # ========================================================
    # DRAG
    # ========================================================

    def begin_drag(
        self,
        event,
    ):
        self._dx = event.x
        self._dy = event.y

        self._drag_distance = 0
        self._dragging = False


        if self._compact_mode():
            self.compact.begin_drag()


    def drag(
        self,
        event,
    ):
        # Compact mode has its own global
        # Windows drag loop.
        if self._compact_mode():
            return


        dx = (
            event.x
            - self._dx
        )

        dy = (
            event.y
            - self._dy
        )


        self._drag_distance += (
            abs(dx)
            + abs(dy)
        )


        if (
            self._drag_distance
            > self.drag_threshold
        ):
            self._dragging = True


        x = (
            self.root.winfo_x()
            + dx
        )

        y = (
            self.root.winfo_y()
            + dy
        )


        self.root.geometry(
            f"+{x}+{y}"
        )


    def end_drag(
        self,
        event,
    ):
        if self._compact_mode():

            compact_distance = (
                self.compact
                .finish_drag()
            )

            self._update_drag_distance(
                compact_distance
            )


        else:
            x = (
                self.root.winfo_x()
            )

            y = (
                self.root.winfo_y()
            )


            self.config[
                "pos_x"
            ] = x

            self.config[
                "pos_y"
            ] = y


            self.compact.set_normal_position(
                x,
                y,
            )


            self._save_config(
                self.config
            )


        if not self._dragging:

            button = (
                self._bubble_button_at(
                    event.x,
                    event.y,
                )
            )


            if button is not None:
                self._on_button(
                    button
                )


        self._dragging = False
        self._drag_distance = 0


    # ========================================================
    # HOVER
    # ========================================================

    def mouse_motion(
        self,
        event,
    ):
        if self._dragging:
            return


        hover = (
            self._bubble_button_at(
                event.x,
                event.y,
            )
        )


        if hover != self._get_hover():
            self._set_hover(
                hover
            )


    def mouse_leave(
        self,
        event=None,
    ):
        if self._get_hover() is not None:
            self._set_hover(
                None
            )
