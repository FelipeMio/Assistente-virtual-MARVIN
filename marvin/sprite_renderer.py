import math
import random
import time


class SpriteRenderer:

    def __init__(
        self,
        canvas,
        *,
        normal_size,
        compact_size,
        blink_min_seconds,
        blink_max_seconds,
        yawn_min_seconds,
        yawn_max_seconds,
        alert_frame_seconds,
        compact_frame_seconds,
    ):
        self.canvas = canvas

        self.normal_width = int(
            normal_size[0]
        )

        self.normal_height = int(
            normal_size[1]
        )

        self.compact_width = int(
            compact_size[0]
        )

        self.compact_height = int(
            compact_size[1]
        )

        self.blink_min_seconds = float(
            blink_min_seconds
        )

        self.blink_max_seconds = float(
            blink_max_seconds
        )

        self.yawn_min_seconds = float(
            yawn_min_seconds
        )

        self.yawn_max_seconds = float(
            yawn_max_seconds
        )

        self.alert_frame_seconds = float(
            alert_frame_seconds
        )

        self.compact_frame_seconds = float(
            compact_frame_seconds
        )

        self.idle_frames = []
        self.alert_frames = []
        self.waiting_frames = []
        self.happy_frame = None
        self.compact_frames = []
        self.yawn_frames = []

        now = time.monotonic()

        self._next_blink = (
            now
            + random.uniform(
                self.blink_min_seconds,
                self.blink_max_seconds,
            )
        )

        self._blink_until = 0.0

        self._next_yawn = (
            now
            + random.uniform(
                self.yawn_min_seconds,
                self.yawn_max_seconds,
            )
        )

        self._yawn_index = 0
        self._yawn_last_frame = 0.0

        self._yawn_sequence = [
            0,
            1,
            1,
            1,
            0,
        ]

        self._alert_frame_index = 0
        self._alert_last_frame = now

        self._compact_frame_index = 0
        self._compact_last_frame = now

        self._compact_sequence = [
            0,
            0,
            0,
            0,
            0,
            2,
            1,
            1,
            1,
            1,
            1,
            2,
            0,
        ]


    # ========================================================
    # ASSETS
    # ========================================================

    def set_assets(
        self,
        assets,
    ):
        self.idle_frames = list(
            assets.get(
                "idle",
                [],
            )
            or []
        )

        self.alert_frames = list(
            assets.get(
                "alert",
                [],
            )
            or []
        )

        self.waiting_frames = list(
            assets.get(
                "waiting",
                [],
            )
            or []
        )

        self.happy_frame = assets.get(
            "happy"
        )

        self.compact_frames = list(
            assets.get(
                "compact",
                [],
            )
            or []
        )

        self.yawn_frames = list(
            assets.get(
                "yawn",
                [],
            )
            or []
        )

        self._alert_frame_index = 0
        self._compact_frame_index = 0


    @property
    def has_idle(self):
        return bool(
            self.idle_frames
        )


    @property
    def has_yawn(self):
        return bool(
            self.yawn_frames
        )


    @property
    def has_happy(self):
        return (
            self.happy_frame
            is not None
        )


    @property
    def has_alert_or_waiting(self):
        return bool(
            self.alert_frames
            or self.waiting_frames
        )


    def reminder_frame_height(self):
        if self.alert_frames:
            return (
                self.alert_frames[0]
                .height()
            )

        if self.waiting_frames:
            return (
                self.waiting_frames[0]
                .height()
            )

        return None


    # ========================================================
    # NORMAL FRAME
    # ========================================================

    def _draw_normal_frame(
        self,
        frame,
        t,
    ):
        self.canvas.delete(
            "all"
        )

        bob = int(
            math.sin(
                t * 1.4
            ) * 3
        )

        x = (
            self.normal_width
            // 2
        )

        bottom_y = (
            self.normal_height
            - 8
            + bob
        )

        top_y = (
            bottom_y
            - frame.height()
        )

        self.canvas.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s",
        )

        return top_y


    # ========================================================
    # IDLE
    # ========================================================

    def draw_idle(
        self,
        t,
    ):
        if not self.idle_frames:
            return None

        now = time.monotonic()

        if (
            now >= self._next_blink
            and now >= self._blink_until
        ):
            self._blink_until = (
                now + 0.14
            )

            self._next_blink = (
                now
                + random.uniform(
                    self.blink_min_seconds,
                    self.blink_max_seconds,
                )
            )


        if (
            now < self._blink_until
            and len(
                self.idle_frames
            ) >= 2
        ):
            frame = (
                self.idle_frames[1]
            )

        else:
            frame = (
                self.idle_frames[0]
            )


        return self._draw_normal_frame(
            frame,
            t,
        )


    # ========================================================
    # YAWN
    # ========================================================

    def yawn_due(
        self,
        now=None,
    ):
        if not self.yawn_frames:
            return False

        if now is None:
            now = time.monotonic()

        return (
            now >= self._next_yawn
        )


    def start_yawn(
        self,
        now=None,
    ):
        if now is None:
            now = time.monotonic()

        self._yawn_index = 0
        self._yawn_last_frame = now


    def _schedule_next_yawn(
        self,
        now=None,
    ):
        if now is None:
            now = time.monotonic()

        self._next_yawn = (
            now
            + random.uniform(
                self.yawn_min_seconds,
                self.yawn_max_seconds,
            )
        )


    def draw_yawn(
        self,
        t,
    ):
        now = time.monotonic()

        if len(
            self.yawn_frames
        ) < 2:
            self._yawn_index = 0
            self._yawn_last_frame = 0.0

            self._schedule_next_yawn(
                now
            )

            return (
                self.draw_idle(t),
                True,
            )


        if self._yawn_last_frame == 0.0:
            self._yawn_last_frame = now


        if (
            now
            - self._yawn_last_frame
            >= 0.32
        ):
            self._yawn_index += 1
            self._yawn_last_frame = now


        if (
            self._yawn_index
            >= len(
                self._yawn_sequence
            )
        ):
            self._yawn_index = 0
            self._yawn_last_frame = 0.0

            self._schedule_next_yawn(
                now
            )

            return (
                self.draw_idle(t),
                True,
            )


        indice = (
            self._yawn_sequence[
                self._yawn_index
            ]
        )

        indice = min(
            indice,
            len(
                self.yawn_frames
            ) - 1,
        )

        frame = (
            self.yawn_frames[
                indice
            ]
        )


        return (
            self._draw_normal_frame(
                frame,
                t,
            ),
            False,
        )


    # ========================================================
    # HAPPY
    # ========================================================

    def draw_happy(
        self,
        t,
    ):
        if self.happy_frame is None:
            return None

        return self._draw_normal_frame(
            self.happy_frame,
            t,
        )


    # ========================================================
    # ALERT
    # ========================================================

    def draw_alert(
        self,
        t,
    ):
        if not self.alert_frames:
            return None

        now = time.monotonic()

        if (
            now
            - self._alert_last_frame
            >= self.alert_frame_seconds
        ):
            self._alert_frame_index = (
                self._alert_frame_index
                + 1
            ) % len(
                self.alert_frames
            )

            self._alert_last_frame = (
                now
            )


        frame = (
            self.alert_frames[
                self._alert_frame_index
            ]
        )


        return self._draw_normal_frame(
            frame,
            t,
        )


    # ========================================================
    # WAITING
    # ========================================================

    def draw_waiting(
        self,
        t,
        indice,
    ):
        if not self.waiting_frames:
            return self.draw_alert(
                t
            )

        indice = max(
            0,
            min(
                int(indice),
                len(
                    self.waiting_frames
                ) - 1,
            ),
        )

        frame = (
            self.waiting_frames[
                indice
            ]
        )


        return self._draw_normal_frame(
            frame,
            t,
        )


    def draw_reminder(
        self,
        t,
        *,
        bubble_mode,
        reminder_started_at,
        waiting_times,
    ):
        if bubble_mode != "alert":
            return self.draw_alert(
                t
            )

        if reminder_started_at is None:
            return self.draw_alert(
                t
            )

        if not self.waiting_frames:
            return self.draw_alert(
                t
            )


        elapsed = (
            time.monotonic()
            - reminder_started_at
        )

        t1, t2, t3 = (
            waiting_times
        )


        if elapsed >= t3:
            return self.draw_waiting(
                t,
                2,
            )

        if elapsed >= t2:
            return self.draw_waiting(
                t,
                1,
            )

        if elapsed >= t1:
            return self.draw_waiting(
                t,
                0,
            )

        return self.draw_alert(
            t
        )


    # ========================================================
    # COMPACT
    # ========================================================

    def reset_compact_animation(
        self,
    ):
        self._compact_frame_index = 0

        self._compact_last_frame = (
            time.monotonic()
        )


    def draw_compact(
        self,
    ):
        if not self.compact_frames:
            return None

        now = time.monotonic()

        if (
            now
            - self._compact_last_frame
            >= self.compact_frame_seconds
        ):
            self._compact_frame_index = (
                self._compact_frame_index
                + 1
            ) % len(
                self._compact_sequence
            )

            self._compact_last_frame = (
                now
            )


        indice = (
            self._compact_sequence[
                self._compact_frame_index
            ]
        )

        indice = min(
            indice,
            len(
                self.compact_frames
            ) - 1,
        )

        frame = (
            self.compact_frames[
                indice
            ]
        )

        self.canvas.delete(
            "all"
        )

        x = (
            self.compact_width
            // 2
        )

        bottom_y = (
            self.compact_height
            - 1
        )

        self.canvas.create_image(
            x,
            bottom_y,
            image=frame,
            anchor="s",
        )

        return (
            bottom_y
            - frame.height()
        )
