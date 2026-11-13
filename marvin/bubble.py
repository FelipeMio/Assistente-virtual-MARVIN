import math
import tkinter.font as tkfont


FONT_FAMILY = "Segoe UI"

PAD_X = 12
PAD_Y = 9
RADIUS = 10
TAIL_HALF = 6
GAP = 16          # distancia entre o balao e a cabeca do MARVIN
MAX_LINES = 4
MIN_WIDTH = 70

PILL_H = 24
PILL_GAP = 6

ALERT_BUTTONS = (
    ("complete", "✓ Concluir", 70),
    ("snooze", "Adiar", 58),
)

SNOOZE_OPTIONS = (
    ("5", "5m"),
    ("15", "15m"),
    ("30", "30m"),
    ("60", "1h"),
)
SNOOZE_PILL_W = 31


class BubbleRenderer:
    """
    Desenha o balao do MARVIN e calcula
    a geometria dos botoes interativos.

    O mesmo layout e usado para desenhar e para o
    hit test dos cliques, entao os dois nunca divergem.
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

        self._fonts = {}

    # ========================================================
    # FONTES
    # ========================================================

    def _font(self, size, weight="normal"):
        key = (size, weight)

        if key not in self._fonts:
            self._fonts[key] = tkfont.Font(
                root=self.canvas,
                family=FONT_FAMILY,
                size=size,
                weight=weight,
            )

        return self._fonts[key]

    def _text_font(self, mode):
        # Lembretes ganham destaque em negrito.
        return self._font(
            9,
            "bold" if mode == "alert" else "normal",
        )

    # ========================================================
    # TEXTO
    # ========================================================

    @staticmethod
    def _wrap(text, font, max_width):
        """Quebra o texto pela largura real em pixels."""
        lines = []

        for paragraph in str(text).split("\n"):
            words = paragraph.split()

            if not words:
                continue

            current = words[0]

            for word in words[1:]:
                candidate = f"{current} {word}"

                if font.measure(candidate) <= max_width:
                    current = candidate
                else:
                    lines.append(current)
                    current = word

            lines.append(current)

        if len(lines) > MAX_LINES:
            lines = lines[:MAX_LINES]
            last = lines[-1]

            while last and font.measure(last + "…") > max_width:
                last = last[:-1]

            lines[-1] = last.rstrip() + "…"

        # Palavras enormes (nomes de arquivo) sao cortadas.
        result = []

        for line in lines:
            while line and font.measure(line) > max_width:
                line = line[:-2] + "…"
            result.append(line)

        return result

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
        font = self._text_font(mode)

        max_bubble_w = max(MIN_WIDTH, self.width - 12)
        max_text_w = max_bubble_w - 2 * PAD_X

        wrapped = self._wrap(text, font, max_text_w)

        if not wrapped:
            return None

        line_h = font.metrics("linespace") + 1

        text_w = max(font.measure(line) for line in wrapped)

        if mode == "alert":
            buttons_w = (
                sum(w for _, _, w in ALERT_BUTTONS)
                + PILL_GAP * (len(ALERT_BUTTONS) - 1)
            )
            buttons_h = PILL_H + 10

        elif mode == "snooze":
            buttons_w = (
                SNOOZE_PILL_W * len(SNOOZE_OPTIONS)
                + PILL_GAP * (len(SNOOZE_OPTIONS) - 1)
            )
            buttons_h = PILL_H + 10 + 18

        else:
            buttons_w = 0
            buttons_h = 0

        bubble_width = min(
            max_bubble_w,
            max(
                MIN_WIDTH,
                text_w + 2 * PAD_X,
                buttons_w + 2 * PAD_X,
            ),
        )

        bubble_height = (
            len(wrapped) * line_h
            + PAD_Y * 2
            + buttons_h
        )

        bubble_x = min(
            max(6, center_x - bubble_width // 2),
            self.width - 6 - bubble_width,
        )

        bubble_y = max(
            6,
            top_y
            - bubble_height
            - GAP,
        )

        layout = {
            "wrapped": wrapped,
            "line_h": line_h,
            "py": PAD_Y,
            "bw": bubble_width,
            "bh": bubble_height,
            "bx": bubble_x,
            "by": bubble_y,
            "button_y": None,
            "buttons": {},
        }

        if mode not in ("alert", "snooze"):
            return layout

        button_y = (
            bubble_y
            + PAD_Y
            + len(wrapped) * line_h
            + 8
        )

        layout["button_y"] = button_y

        if mode == "alert":
            specs = [(key, label, w) for key, label, w in ALERT_BUTTONS]
        else:
            specs = [
                (key, label, SNOOZE_PILL_W)
                for key, label in SNOOZE_OPTIONS
            ]

        total = (
            sum(w for _, _, w in specs)
            + PILL_GAP * (len(specs) - 1)
        )

        x = bubble_x + (bubble_width - total) / 2

        for key, label, w in specs:
            layout["buttons"][key] = {
                "label": label,
                "box": (x, button_y, x + w, button_y + PILL_H),
            }
            x += w + PILL_GAP

        if mode == "snooze":
            back_y = button_y + PILL_H + 13
            cx = bubble_x + bubble_width / 2

            layout["back_y"] = back_y
            layout["buttons"]["back"] = {
                "label": "↩ voltar",
                "box": (cx - 34, back_y - 9, cx + 34, back_y + 9),
                "link": True,
            }

        return layout

    # ========================================================
    # FORMAS
    # ========================================================

    @staticmethod
    def _rounded_points(x1, y1, x2, y2, r, tail=None):
        """
        Pontos de um retangulo arredondado (smooth=True).

        Pontos duplicados viram cantos/segmentos retos;
        os cantos simples viram curvas. `tail` = (base_x, tip_y)
        acrescenta a ponta do balao na borda de baixo.
        """
        pts = [
            x1 + r, y1, x1 + r, y1,
            x2 - r, y1, x2 - r, y1,
            x2, y1,
            x2, y1 + r, x2, y1 + r,
            x2, y2 - r, x2, y2 - r,
            x2, y2,
            x2 - r, y2, x2 - r, y2,
        ]

        if tail is not None:
            tx, ty = tail
            pts += [
                tx + TAIL_HALF, y2, tx + TAIL_HALF, y2,
                tx, ty, tx, ty,
                tx - TAIL_HALF, y2, tx - TAIL_HALF, y2,
            ]

        pts += [
            x1 + r, y2, x1 + r, y2,
            x1, y2,
            x1, y2 - r, x1, y2 - r,
            x1, y1 + r, x1, y1 + r,
            x1, y1,
        ]

        return pts

    def _pill(self, box, *, fill, outline, text, text_color, font):
        x1, y1, x2, y2 = box
        r = (y2 - y1) / 2

        self.canvas.create_polygon(
            self._rounded_points(x1, y1, x2, y2, r),
            smooth=True,
            fill=fill,
            outline=outline,
            width=1,
        )

        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill=text_color,
            font=font,
        )

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

        bx = layout["bx"]
        by = layout["by"]
        bw = layout["bw"]
        bh = layout["bh"]

        tip_x = min(
            max(center_x, bx + RADIUS + TAIL_HALF + 2),
            bx + bw - RADIUS - TAIL_HALF - 2,
        )

        # Corpo + ponta num unico contorno continuo.
        self.canvas.create_polygon(
            self._rounded_points(
                bx,
                by,
                bx + bw,
                by + bh,
                RADIUS,
                tail=(tip_x, top_y - 3),
            ),
            smooth=True,
            fill=colors["bub_bg"],
            outline=colors["bub_bd"],
            width=2,
        )

        # Texto
        font = self._text_font(mode)
        line_h = layout["line_h"]
        text_y = by + PAD_Y

        for index, line in enumerate(layout["wrapped"]):
            self.canvas.create_text(
                bx + bw / 2,
                text_y + index * line_h + line_h / 2,
                text=line,
                fill=colors["text"],
                font=font,
                anchor="center",
            )

        if mode == "alert":
            self._draw_alert_buttons(layout, hover)

        elif mode == "snooze":
            self._draw_snooze_buttons(layout, hover)

    def _draw_alert_buttons(
        self,
        layout,
        hover,
    ):
        colors = self.palette
        font = self._font(8, "bold")

        estilos = {
            # botao: (cor principal)
            "complete": colors["green"],
            "snooze": colors["accent"],
        }

        for key, button in layout["buttons"].items():
            cor = estilos[key]
            ativo = hover == key

            self._pill(
                button["box"],
                fill=cor if ativo else colors["bub_bg"],
                outline=cor,
                text=button["label"],
                text_color="#FFFFFF" if ativo else cor,
                font=font,
            )

    def _draw_snooze_buttons(
        self,
        layout,
        hover,
    ):
        colors = self.palette
        font = self._font(8, "bold")

        for key, button in layout["buttons"].items():
            ativo = hover == key

            if button.get("link"):
                x1, y1, x2, y2 = button["box"]

                self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=button["label"],
                    fill=colors["accent"] if ativo else colors["dim"],
                    font=self._font(8),
                )
                continue

            self._pill(
                button["box"],
                fill=colors["accent"] if ativo else colors["bub_bg"],
                outline=colors["accent"],
                text=button["label"],
                text_color="#FFFFFF" if ativo else colors["accent"],
                font=font,
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

        # Margem extra deixa os botoes faceis de acertar,
        # mesmo com o MARVIN balancando.
        folga = 3

        for key, button in layout["buttons"].items():
            x1, y1, x2, y2 = button["box"]

            if (
                x1 - folga <= x <= x2 + folga
                and y1 - folga <= y <= y2 + folga
            ):
                return key

        return None
