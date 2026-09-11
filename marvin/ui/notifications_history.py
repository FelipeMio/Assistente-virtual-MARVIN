from datetime import datetime

import customtkinter as ctk

from marvin.config import load_cfg
from marvin.theme import get_modern_palette


class NotificationHistoryWindow:

    WIDTH = 360
    HEIGHT = 545

    def __init__(
        self,
        parent,
        companion,
        on_change=None,
        on_close=None,
        position=None,
    ):
        self.parent = parent
        self.comp = companion

        self.on_change = on_change
        self.on_close = on_close
        self.position = position

        self._drag_x = 0
        self._drag_y = 0

        self._confirm_clear = False
        self._confirm_job = None

        config = load_cfg()

        self.tema = config.get(
            "tema",
            "escuro",
        )

        self.colors = get_modern_palette(
            self.tema,
            "home",
        )

        self.win = ctk.CTkToplevel(
            parent
        )

        self.win.title(
            "MARVIN"
        )

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.resizable(
            False,
            False,
        )

        # Mesmo comportamento visual da Central.
        self.win.overrideredirect(
            True
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self._build()
        self.refresh()

        self.win.after(
            30,
            self._place_window,
        )

    # ========================================================
    # JANELA
    # ========================================================

    def _place_window(self):
        try:
            self.win.update_idletasks()

            if self.position:
                x, y = self.position

            else:
                x = (
                    self.parent.winfo_x()
                )

                y = (
                    self.parent.winfo_y()
                )

            self.win.geometry(
                f"{self.WIDTH}x{self.HEIGHT}"
                f"+{x}+{y}"
            )

            self.win.deiconify()
            self.win.lift()
            self.win.focus_force()

        except Exception:
            pass

    def _drag_start(
        self,
        event,
    ):
        self._drag_x = (
            event.x_root
            - self.win.winfo_x()
        )

        self._drag_y = (
            event.y_root
            - self.win.winfo_y()
        )

    def _drag_move(
        self,
        event,
    ):
        x = (
            event.x_root
            - self._drag_x
        )

        y = (
            event.y_root
            - self._drag_y
        )

        self.win.geometry(
            f"+{x}+{y}"
        )

    def close(self):
        try:
            self.comp._notifications_window = None
        except Exception:
            pass

        try:
            if callable(
                self.on_change
            ):
                self.on_change()

        except Exception:
            pass

        try:
            self.win.destroy()
        except Exception:
            pass

        try:
            if callable(
                self.on_close
            ):
                self.on_close()

        except Exception:
            pass

    # ========================================================
    # HELPERS VISUAIS
    # ========================================================

    def _divider(
        self,
        parent,
    ):
        return ctk.CTkFrame(
            parent,
            height=1,
            corner_radius=0,
            fg_color=self.colors[
                "border"
            ],
        )

    def _preview_message(
        self,
        message,
    ):
        message = str(
            message or ""
        ).strip()

        lines = [
            line.strip()
            for line
            in message.splitlines()
            if line.strip()
        ]

        if len(lines) > 4:
            lines = lines[:4]
            lines.append("...")

        text = "\n".join(lines)

        if len(text) > 230:
            text = (
                text[:227]
                + "..."
            )

        return text

    def _format_time(
        self,
        value,
    ):
        try:
            dt = datetime.fromisoformat(
                value
            )

            hoje = datetime.now(
                dt.tzinfo
            ).date()

            if dt.date() == hoje:
                return dt.strftime(
                    "Hoje, %H:%M"
                )

            return dt.strftime(
                "%d/%m/%Y, %H:%M"
            )

        except Exception:
            return str(
                value or ""
            )

    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self):

        self.shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["bg"],
            border_width=1,
            border_color=self.colors[
                "border"
            ],
            corner_radius=16,
        )

        self.shell.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1,
        )

        # ====================================================
        # TITLEBAR
        # ====================================================

        titlebar = ctk.CTkFrame(
            self.shell,
            height=45,
            fg_color="transparent",
            corner_radius=0,
        )

        titlebar.pack(
            fill="x",
        )

        titlebar.pack_propagate(
            False
        )

        titlebar.bind(
            "<ButtonPress-1>",
            self._drag_start,
        )

        titlebar.bind(
            "<B1-Motion>",
            self._drag_move,
        )

        left = ctk.CTkFrame(
            titlebar,
            fg_color="transparent",
        )

        left.pack(
            side="left",
            padx=14,
        )

        mark = ctk.CTkFrame(
            left,
            width=21,
            height=21,
            corner_radius=6,
            fg_color=self.colors[
                "accent"
            ],
        )

        mark.pack(
            side="left",
        )

        mark.pack_propagate(
            False
        )

        ctk.CTkLabel(
            mark,
            text="",
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        title_label = ctk.CTkLabel(
            left,
            text="MARVIN",
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        )

        title_label.pack(
            side="left",
            padx=(8, 0),
        )

        title_label.bind(
            "<ButtonPress-1>",
            self._drag_start,
        )

        title_label.bind(
            "<B1-Motion>",
            self._drag_move,
        )

        ctk.CTkButton(
            titlebar,
            text="X",
            width=28,
            height=28,
            corner_radius=7,
            fg_color="transparent",
            hover_color=self.colors[
                "button_hover"
            ],
            text_color=self.colors[
                "dim"
            ],
            border_width=0,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
            command=self.close,
        ).pack(
            side="right",
            padx=(2, 10),
        )

        self._divider(
            self.shell
        ).pack(
            fill="x",
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            self.shell,
            fg_color="transparent",
        )

        header.pack(
            fill="x",
            padx=17,
            pady=(14, 11),
        )

        top_line = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        top_line.pack(
            fill="x",
        )

        ctk.CTkButton(
            top_line,
            text="<",
            width=27,
            height=27,
            corner_radius=7,
            fg_color="transparent",
            hover_color=self.colors[
                "button_hover"
            ],
            border_width=1,
            border_color=self.colors[
                "border"
            ],
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold",
            ),
            command=self.close,
        ).pack(
            side="left",
        )

        ctk.CTkLabel(
            top_line,
            text="Notifica\u00e7\u00f5es",
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold",
            ),
        ).pack(
            side="left",
            padx=(10, 0),
        )

        self.count_label = (
            ctk.CTkLabel(
                top_line,
                text="",
                text_color=self.colors[
                    "accent"
                ],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                    weight="bold",
                ),
            )
        )

        self.count_label.pack(
            side="right",
        )

        self.subtitle = ctk.CTkLabel(
            header,
            text=(
                "Hist\u00f3rico de avisos "
                "recebidos"
            ),
            text_color=self.colors[
                "dim"
            ],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
        )

        self.subtitle.pack(
            fill="x",
            pady=(6, 0),
        )

        self._divider(
            self.shell
        ).pack(
            fill="x",
        )

        # ====================================================
        # LISTA
        # ====================================================

        self.list_frame = (
            ctk.CTkScrollableFrame(
                self.shell,
                fg_color="transparent",
                corner_radius=0,
            )
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        # ====================================================
        # FOOTER
        # ====================================================

        self._divider(
            self.shell
        ).pack(
            fill="x",
        )

        self.footer = ctk.CTkFrame(
            self.shell,
            height=56,
            fg_color="transparent",
        )

        self.footer.pack(
            fill="x",
            padx=11,
            pady=9,
        )

        self.footer.pack_propagate(
            False
        )

        self.mark_all_button = (
            ctk.CTkButton(
                self.footer,
                text=(
                    "Marcar todas"
                ),
                height=34,
                corner_radius=8,
                fg_color=self.colors[
                    "accent"
                ],
                hover_color=self.colors[
                    "accent_hover"
                ],
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                    weight="bold",
                ),
                command=self._mark_all,
            )
        )

        self.mark_all_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )

        self.clear_button = (
            ctk.CTkButton(
                self.footer,
                text=(
                    "Limpar"
                ),
                width=90,
                height=34,
                corner_radius=8,
                fg_color="transparent",
                hover_color=self.colors[
                    "button_hover"
                ],
                border_width=1,
                border_color=self.colors[
                    "border"
                ],
                text_color=self.colors[
                    "dim"
                ],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=10,
                ),
                command=self._clear_clicked,
            )
        )

        self.clear_button.pack(
            side="right",
            padx=(4, 0),
        )

    # ========================================================
    # ACOES
    # ========================================================

    def _changed(self):
        try:
            if callable(
                self.on_change
            ):
                self.on_change()

        except Exception:
            pass

    def _mark_read(
        self,
        notification_id,
    ):
        try:
            self.comp.notifications.marcar_como_lida(
                notification_id
            )
        except Exception:
            pass

        self.refresh()
        self._changed()

    def _mark_all(self):
        try:
            self.comp.notifications.marcar_todas_como_lidas()
        except Exception:
            pass

        self.refresh()
        self._changed()

    def _reset_clear_button(self):
        self._confirm_clear = False
        self._confirm_job = None

        try:
            self.clear_button.configure(
                text="Limpar"
            )
        except Exception:
            pass

    def _clear_clicked(self):
        if not self._confirm_clear:
            self._confirm_clear = True

            self.clear_button.configure(
                text="Confirmar"
            )

            try:
                if self._confirm_job:
                    self.win.after_cancel(
                        self._confirm_job
                    )
            except Exception:
                pass

            self._confirm_job = (
                self.win.after(
                    3000,
                    self._reset_clear_button,
                )
            )

            return

        try:
            self.comp.notifications.limpar()
        except Exception:
            pass

        self._reset_clear_button()

        self.refresh()
        self._changed()

    # ========================================================
    # DADOS
    # ========================================================

    def refresh(self):

        for widget in (
            self.list_frame
            .winfo_children()
        ):
            widget.destroy()

        manager = getattr(
            self.comp,
            "notifications",
            None,
        )

        itens = []
        unread = 0

        if manager is not None:
            try:
                itens = manager.listar(
                    limite=100
                )

                unread = (
                    manager
                    .quantidade_nao_lidas()
                )

            except Exception:
                pass

        total = len(itens)

        if unread == 1:
            count_text = "1 nova"

        else:
            count_text = (
                f"{unread} novas"
            )

        self.count_label.configure(
            text=count_text
        )

        self._update_footer(
            total,
            unread,
        )

        if not itens:
            self._build_empty()
            return

        for index, item in enumerate(
            itens
        ):
            self._build_item(
                item
            )

            if index < len(itens) - 1:
                ctk.CTkFrame(
                    self.list_frame,
                    height=1,
                    corner_radius=0,
                    fg_color=self.colors[
                        "border"
                    ],
                ).pack(
                    fill="x",
                    padx=8,
                    pady=2,
                )

    def _update_footer(
        self,
        total,
        unread,
    ):
        # Sem historico: nao ha nenhuma
        # acao util para mostrar.
        if total == 0:
            try:
                self.footer.pack_forget()
            except Exception:
                pass

            return

        # Garante que o rodape esteja visivel.
        try:
            if not self.footer.winfo_manager():
                self.footer.pack(
                    fill="x",
                    padx=11,
                    pady=9,
                )
        except Exception:
            pass

        # Reorganiza os botoes a cada refresh.
        try:
            self.mark_all_button.pack_forget()
        except Exception:
            pass

        try:
            self.clear_button.pack_forget()
        except Exception:
            pass

        # Existem notificacoes nao lidas:
        # mostra as duas acoes.
        if unread > 0:
            self.mark_all_button.configure(
                state="normal",
                text="Marcar todas como lidas",
            )

            self.mark_all_button.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 4),
            )

            self.clear_button.configure(
                text="Limpar",
                width=90,
            )

            self.clear_button.pack(
                side="right",
                padx=(4, 0),
            )

        # Todas ja foram lidas:
        # so faz sentido manter Limpar historico.
        else:
            self.clear_button.configure(
                text="Limpar historico",
                width=0,
            )

            self.clear_button.pack(
                fill="x",
                expand=True,
            )


    def _build_empty(self):
        empty = ctk.CTkFrame(
            self.list_frame,
            fg_color="transparent",
        )

        empty.pack(
            fill="both",
            expand=True,
            pady=70,
        )

        ctk.CTkLabel(
            empty,
            text="!",
            width=34,
            height=34,
            corner_radius=10,
            fg_color=self.colors[
                "ext_bg"
            ],
            text_color=self.colors[
                "ext_fg"
            ],
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        ).pack()

        ctk.CTkLabel(
            empty,
            text=(
                "Nenhuma notifica\u00e7\u00e3o"
            ),
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        ).pack(
            pady=(10, 2),
        )

        ctk.CTkLabel(
            empty,
            text=(
                "Os avisos do MARVIN "
                "aparecer\u00e3o aqui."
            ),
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        ).pack()

    def _build_item(
        self,
        item,
    ):
        read = bool(
            item.get(
                "lida",
                False,
            )
        )

        card = ctk.CTkFrame(
            self.list_frame,
            fg_color="transparent",
        )

        card.pack(
            fill="x",
            padx=7,
            pady=7,
        )

        top = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        top.pack(
            fill="x",
        )

        origin = str(
            item.get(
                "origem",
                "MARVIN",
            )
        )

        ctk.CTkLabel(
            top,
            text=origin,
            text_color=self.colors[
                "text"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),
        ).pack(
            side="left",
        )

        if not read:
            ctk.CTkLabel(
                top,
                text="NOVA",
                text_color=self.colors[
                    "accent"
                ],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                    weight="bold",
                ),
            ).pack(
                side="right",
            )

        title = str(
            item.get(
                "titulo",
                "Notifica\u00e7\u00e3o",
            )
        )

        ctk.CTkLabel(
            card,
            text=title,
            text_color=self.colors[
                "text"
            ],
            justify="left",
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        ).pack(
            fill="x",
            pady=(5, 2),
        )

        message = self._preview_message(
            item.get(
                "mensagem",
                "",
            )
        )

        if message:
            ctk.CTkLabel(
                card,
                text=message,
                text_color=self.colors[
                    "dim"
                ],
                justify="left",
                anchor="w",
                wraplength=290,
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=9,
                ),
            ).pack(
                fill="x",
                pady=(1, 5),
            )

        bottom = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        bottom.pack(
            fill="x",
            pady=(3, 0),
        )

        ctk.CTkLabel(
            bottom,
            text=self._format_time(
                item.get(
                    "criada_em",
                    "",
                )
            ),
            text_color=self.colors[
                "dim"
            ],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),
        ).pack(
            side="left",
        )

        notification_id = (
            item.get("id")
        )

        if (
            not read
            and notification_id
        ):
            ctk.CTkButton(
                bottom,
                text="Marcar lida",
                width=76,
                height=23,
                corner_radius=6,
                fg_color="transparent",
                hover_color=self.colors[
                    "button_hover"
                ],
                border_width=1,
                border_color=self.colors[
                    "border"
                ],
                text_color=self.colors[
                    "text"
                ],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=8,
                ),
                command=(
                    lambda nid=notification_id:
                    self._mark_read(nid)
                ),
            ).pack(
                side="right",
            )


def abrir_notificacoes(
    parent,
    companion,
    on_change=None,
    on_close=None,
    position=None,
):
    existente = getattr(
        companion,
        "_notifications_window",
        None,
    )

    try:
        if (
            existente is not None
            and existente.win.winfo_exists()
        ):
            existente.on_change = on_change
            existente.on_close = on_close

            if position:
                existente.position = position

            existente.refresh()

            existente.win.deiconify()
            existente.win.lift()
            existente.win.focus_force()

            return existente

    except Exception:
        pass

    janela = NotificationHistoryWindow(
        parent,
        companion,
        on_change=on_change,
        on_close=on_close,
        position=position,
    )

    companion._notifications_window = (
        janela
    )

    return janela
