import math
import textwrap


class BubbleRenderer:
    """
    Desenha o balao do MARVIN e calcula
    a geometria dos botoes interativos.
    """

    def __init__(
        self,
        canvas,
        *,
        palette,
        normal_size,
    ):
        self.canvas = canvas
        self.palette = palette

        self.width = int(
            normal_size[0]
        )

        self.height = int(
            normal_size[1]
        )


    # ========================================================
    # LAYOUT
    # ========================================================

    def layout(
        self,
        text,
        center_x,
        top_y,
        mode="normal",
    ):
        wrapped = textwrap.wrap(
            text,
            width=26,
        )[:4]


        if not wrapped:
            return None


        line_h = 15
        padding_y = 9


        if mode == "alert":
            button_h = 34

        elif mode == "snooze":
            button_h = 54

        else:
            button_h = 0


        bubble_width = max(
            1,
            self.width - 12,
        )


        bubble_height = (
            len(wrapped) * line_h
            + padding_y * 2
            + button_h
        )


        bubble_x = max(
            6,
            center_x
            - bubble_width // 2,
        )


        bubble_y = max(
            6,
            top_y
            - bubble_height
            - 16,
        )


        layout = {
            "wrapped": wrapped,
            "line_h": line_h,
            "py": padding_y,
            "bw": bubble_width,
            "bh": bubble_height,
            "bx": bubble_x,
            "by": bubble_y,
            "button_y": None,
        }


        if mode in (
            "alert",
            "snooze",
        ):
            layout["button_y"] = (
                bubble_y
                + padding_y
                + len(wrapped) * line_h
                + 5
            )


        if mode == "alert":
            layout["complete_x"] = (
                bubble_x
                + bubble_width // 3
            )

            layout["snooze_x"] = (
                bubble_x
                + (
                    bubble_width * 2
                ) // 3
            )


        elif mode == "snooze":
            spacing = (
                bubble_width / 4
            )

            layout["option_x"] = {
                value: (
                    bubble_x
                    + spacing * index
                    + spacing / 2
                )
                for index, value
                in enumerate(
                    (
                        "5",
                        "15",
                        "30",
                        "60",
                    )
                )
            }

            layout["back_y"] = (
                layout["button_y"]
                + 31
            )


        return layout


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        *,
        top_y,
        text,
        mode="normal",
        hover=None,
    ):
        center_x = (
            self.width // 2
        )


        layout = self.layout(
            text,
            center_x,
            top_y,
            mode,
        )


        if layout is None:
            return


        colors = self.palette

        wrapped = layout[
            "wrapped"
        ]

        line_h = layout[
            "line_h"
        ]

        padding_y = layout[
            "py"
        ]

        bubble_width = layout[
            "bw"
        ]

        bubble_height = layout[
            "bh"
        ]

        bubble_x = layout[
            "bx"
        ]

        bubble_y = layout[
            "by"
        ]


        # Shadow.
        self.canvas.create_rectangle(
            bubble_x + 2,
            bubble_y + 2,
            bubble_x + bubble_width + 2,
            bubble_y + bubble_height + 2,
            fill="#060c14",
            outline="",
        )


        # Bubble body.
        self.canvas.create_rectangle(
            bubble_x,
            bubble_y,
            bubble_x + bubble_width,
            bubble_y + bubble_height,
            fill=colors["bub_bg"],
            outline=colors["bub_bd"],
            width=2,
        )


        # Bubble tip.
        tip = min(
            max(
                center_x,
                bubble_x + 16,
            ),
            bubble_x
            + bubble_width
            - 16,
        )


        self.canvas.create_polygon(
            [
                tip - 7,
                bubble_y + bubble_height,

                tip + 7,
                bubble_y + bubble_height,

                tip,
                top_y - 2,
            ],
            fill=colors["bub_bg"],
            outline=colors["bub_bd"],
        )


        self.canvas.create_line(
            bubble_x + 2,
            bubble_y + bubble_height,
            tip - 7,
            bubble_y + bubble_height,
            fill=colors["bub_bd"],
            width=2,
        )


        self.canvas.create_line(
            tip + 7,
            bubble_y + bubble_height,
            bubble_x + bubble_width - 2,
            bubble_y + bubble_height,
            fill=colors["bub_bd"],
            width=2,
        )


        # Text.
        text_y = (
            bubble_y
            + padding_y
        )


        for index, line in enumerate(
            wrapped
        ):
            self.canvas.create_text(
                bubble_x
                + bubble_width // 2,

                text_y
                + index * line_h
                + line_h // 2,

                text=line,
                fill=colors["text"],
                font=(
                    "Consolas",
                    8,
                ),
                anchor="center",
            )


        if mode == "alert":
            self._draw_alert_buttons(
                layout,
                hover,
            )


        elif mode == "snooze":
            self._draw_snooze_buttons(
                layout,
                hover,
            )


    def _draw_alert_buttons(
        self,
        layout,
        hover,
    ):
        colors = self.palette

        button_y = layout[
            "button_y"
        ]

        complete_x = layout[
            "complete_x"
        ]

        snooze_x = layout[
            "snooze_x"
        ]


        complete_active = (
            hover == "complete"
        )


        self.canvas.create_oval(
            complete_x - 11,
            button_y,
            complete_x + 11,
            button_y + 22,
            fill=(
                colors["green"]
                if complete_active
                else colors["panel"]
            ),
            outline=colors["green"],
            width=2,
        )


        self.canvas.create_text(
            complete_x,
            button_y + 11,
            text="✓",
            fill="#ffffff",
            font=(
                "Consolas",
                11,
                "bold",
            ),
        )


        self.canvas.create_text(
            complete_x,
            button_y + 29,
            text="concluir",
            fill=colors["dim"],
            font=(
                "Consolas",
                7,
            ),
        )


        snooze_active = (
            hover == "snooze"
        )


        self.canvas.create_oval(
            snooze_x - 11,
            button_y,
            snooze_x + 11,
            button_y + 22,
            fill=(
                colors["accent"]
                if snooze_active
                else colors["panel"]
            ),
            outline=colors["accent"],
            width=2,
        )


        self.canvas.create_text(
            snooze_x,
            button_y + 11,
            text="⏰",
            fill="#ffffff",
            font=(
                "Segoe UI Symbol",
                9,
            ),
        )


        self.canvas.create_text(
            snooze_x,
            button_y + 29,
            text="adiar",
            fill=colors["dim"],
            font=(
                "Consolas",
                7,
            ),
        )


    def _draw_snooze_buttons(
        self,
        layout,
        hover,
    ):
        colors = self.palette

        button_y = layout[
            "button_y"
        ]


        options = [
            (
                "5",
                "5m",
            ),
            (
                "15",
                "15m",
            ),
            (
                "30",
                "30m",
            ),
            (
                "60",
                "1h",
            ),
        ]


        for value, label in options:

            x = (
                layout[
                    "option_x"
                ][value]
            )

            active = (
                hover == value
            )


            self.canvas.create_oval(
                x - 14,
                button_y,
                x + 14,
                button_y + 24,
                fill=(
                    colors["accent"]
                    if active
                    else colors["panel"]
                ),
                outline=colors["accent"],
                width=1,
            )


            self.canvas.create_text(
                x,
                button_y + 12,
                text=label,
                fill="#ffffff",
                font=(
                    "Consolas",
                    7,
                    "bold",
                ),
            )


        back_y = layout[
            "back_y"
        ]


        active = (
            hover == "back"
        )


        self.canvas.create_text(
            layout["bx"]
            + layout["bw"] // 2,

            back_y,

            text="↩ voltar",

            fill=(
                colors["accent"]
                if active
                else colors["dim"]
            ),

            font=(
                "Consolas",
                7,
                "bold",
            ),
        )


    # ========================================================
    # HIT TEST
    # ========================================================

    def button_at(
        self,
        x,
        y,
        *,
        t,
        text,
        mode,
        sprite_height=None,
    ):
        if mode not in (
            "alert",
            "snooze",
        ):
            return None


        if not text:
            return None


        bob = int(
            math.sin(
                t * 1.4
            ) * 3
        )


        if sprite_height is not None:
            top_y = (
                self.height
                - 8
                + bob
                - sprite_height
            )

        else:
            top_y = (
                self.height
                - 8
                + bob
            )


        layout = self.layout(
            text,
            self.width // 2,
            top_y,
            mode,
        )


        if layout is None:
            return None


        bubble_x = layout[
            "bx"
        ]

        bubble_width = layout[
            "bw"
        ]

        button_y = layout[
            "button_y"
        ]


        if mode == "alert":

            complete_x = layout[
                "complete_x"
            ]

            snooze_x = layout[
                "snooze_x"
            ]


            if (
                (
                    x - complete_x
                ) ** 2
                + (
                    y
                    - (
                        button_y + 11
                    )
                ) ** 2
                <= 16 ** 2
            ):
                return "complete"


            if (
                (
                    x - snooze_x
                ) ** 2
                + (
                    y
                    - (
                        button_y + 11
                    )
                ) ** 2
                <= 16 ** 2
            ):
                return "snooze"


        elif mode == "snooze":

            for value, x_button in (
                layout[
                    "option_x"
                ].items()
            ):

                if (
                    (
                        x - x_button
                    ) ** 2
                    + (
                        y
                        - (
                            button_y + 12
                        )
                    ) ** 2
                    <= 18 ** 2
                ):
                    return value


            back_y = layout[
                "back_y"
            ]


            if (
                abs(
                    x
                    - (
                        bubble_x
                        + bubble_width // 2
                    )
                ) <= 45

                and abs(
                    y - back_y
                ) <= 12
            ):
                return "back"


        return None
