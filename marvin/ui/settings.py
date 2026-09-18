import os
import sys
import tkinter as tk

import customtkinter as ctk

from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageTk

from ..config import save_cfg
from ..theme import get_modern_palette


class SettingsWindow:

    WIDTH = 430
    HEIGHT = 680

    def __init__(
        self,
        parent,
        companion,
        *,
        config,
        positioner,
        startup_enabled,
        set_startup_enabled,
        idle_frequency_options,
        idle_frequency_label,
        idle_msgs,
        waiting_phrases_factory,
        db_path,
        db_cleaner,
    ):
        self.comp = companion

        self.cfg = config

        self._positioner = positioner
        self._startup_enabled = startup_enabled
        self._set_startup_enabled = set_startup_enabled

        self._idle_frequency_options = (
            idle_frequency_options
        )

        self._idle_frequency_label = (
            idle_frequency_label
        )

        self._idle_msgs = idle_msgs

        self._waiting_phrases_factory = (
            waiting_phrases_factory
        )

        self._db_path = db_path
        self._db_cleaner = db_cleaner

        tema = self.cfg.get("tema", "escuro")

        self.colors = get_modern_palette(tema, "settings")

        self.win = ctk.CTkToplevel(parent)

        self.win.withdraw()
        self.win.overrideredirect(True)

        self.win.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )

        self.win.configure(
            fg_color=self.colors["bg"]
        )

        self.win.transient(parent)

        self._drag_x = 0
        self._drag_y = 0

        self._build()

        self.win.update_idletasks()

        self._positioner(
            self.win,
            self.comp
        )

        self.win.deiconify()
        self.win.lift()
        self.win.grab_set()
        self.win.focus_force()

        self.win.bind(
            "<Escape>",
            lambda e: self.win.destroy()
        )

    # ==========================================================
    # JANELA
    # ==========================================================

    def _drag_start(self, event):
        self._drag_x = (
            event.x_root
            - self.win.winfo_x()
        )

        self._drag_y = (
            event.y_root
            - self.win.winfo_y()
        )

    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y

        self.win.geometry(
            f"+{x}+{y}"
        )

    # ==========================================================
    # COMPONENTES
    # ==========================================================

    def _section_title(
        self,
        parent,
        texto
    ):
        ctk.CTkLabel(
            parent,
            text=texto.upper(),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        ).pack(
            fill="x",
            pady=(18, 7)
        )

    def _toggle_row(
        self,
        parent,
        titulo,
        descricao,
        variable
    ):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=12,
            pady=10
        )

        text_area = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )

        text_area.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            text_area,
            text=titulo,
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            )
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            text_area,
            text=descricao,
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9
            )
        ).pack(
            fill="x",
            pady=(1, 0)
        )

        switch = ctk.CTkSwitch(
            row,
            text="",
            variable=variable,
            width=42,
            progress_color=self.colors["accent"],
            button_color=self.colors["card"],
            button_hover_color=self.colors["accent_hover"]
        )

        switch.pack(
            side="right",
            padx=(12, 0)
        )

    def _slider_block(
        self,
        parent,
        titulo,
        variable,
        from_,
        to,
        steps,
        valor,
        command
    ):
        block = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        block.pack(
            fill="x",
            pady=(0, 14)
        )

        top = ctk.CTkFrame(
            block,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            pady=(0, 7)
        )

        ctk.CTkLabel(
            top,
            text=titulo,
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            )
        ).pack(
            side="left"
        )

        badge = ctk.CTkLabel(
            top,
            text=valor,
            width=50,
            height=24,
            corner_radius=7,
            fg_color=self.colors["surface"],
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        )

        badge.pack(
            side="right"
        )

        slider = ctk.CTkSlider(
            block,
            variable=variable,
            from_=from_,
            to=to,
            number_of_steps=steps,
            fg_color=self.colors["border"],
            progress_color=self.colors["accent"],
            button_color=self.colors["card"],
            button_hover_color=self.colors["accent_hover"],
            height=18,
            command=lambda value: command(
                value,
                badge
            )
        )

        slider.pack(
            fill="x"
        )

        # CustomTkinter nao rola o CTkScrollableFrame quando
        # o cursor esta sobre um CTkSlider.
        # Redirecionamos esse evento para o scroll da pagina.
        slider.bind(
            "<MouseWheel>",
            self._scroll_settings_from_control,
            add="+"
        )

        return slider

    # ==========================================================
    # CALLBACKS VISUAIS
    # ==========================================================

    def _tema_visual_changed(self, valor):
        if valor == "Claro":
            self.v_tema.set("claro")
        else:
            self.v_tema.set("escuro")

    def _toggle_size_edit(self):
        """
        Os controles de tamanho so podem ser alterados
        quando 'Editar tamanho' estiver marcado.
        """

        enabled = bool(
            self.v_edit_size.get()
        )

        state = (
            "normal"
            if enabled
            else "disabled"
        )

        for slider in (
            getattr(
                self,
                "size_normal_slider",
                None
            ),
            getattr(
                self,
                "size_compact_slider",
                None
            ),
            getattr(
                self,
                "opacity_slider",
                None
            ),
        ):
            if slider is None:
                continue

            slider.configure(
                state=state,
                progress_color=(
                    self.colors["accent"]
                    if enabled
                    else self.colors["border"]
                ),
                button_color=(
                    self.colors["card"]
                    if enabled
                    else self.colors["surface"]
                ),
                button_hover_color=(
                    self.colors["accent_hover"]
                    if enabled
                    else self.colors["surface"]
                )
            )

        if (
            not enabled
            and hasattr(
                self,
                "size_preview_image_label"
            )
        ):
            self._clear_size_preview()


    def _clear_size_preview(self):
        """
        Limpa a demonstracao visual dos tamanhos.
        """

        if not hasattr(
            self,
            "size_preview_image_label"
        ):
            return

        self._size_preview_photo = None

        self.size_preview_image_label.configure(
            image=None,
            text=(
                "Mova um dos controles de tamanho "
                "para visualizar."
            )
        )

        self.size_preview_title.configure(
            text="Prévia — ajuste um tamanho"
        )


    def _update_size_preview(
        self,
        modo,
        valor
    ):
        """
        Mostra nas Configuracoes uma demonstracao do
        tamanho real do MARVIN sem trocar o modo atual.
        """

        if not bool(
            self.v_edit_size.get()
        ):
            return

        try:
            percentual = int(
                round(float(valor))
            )
        except (TypeError, ValueError):
            return

        percentual = max(
            60,
            min(120, percentual)
        )

        base = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "assets"
            / "marvin"
        )

        try:

            # ==================================================
            # MODO NORMAL
            # Mesma regra do MARVIN:
            # 150 px no tamanho 100%.
            # ==================================================

            if modo == "normal":

                arquivo = (
                    base
                    / "idle"
                    / "01.png"
                )

                if not arquivo.exists():
                    raise FileNotFoundError(
                        arquivo
                    )

                imagem = (
                    Image.open(arquivo)
                    .convert("RGBA")
                )

                tamanho = max(
                    1,
                    int(
                        150
                        * percentual
                        / 100
                    )
                )

                imagem = imagem.resize(
                    (
                        tamanho,
                        tamanho
                    ),
                    Image.Resampling.NEAREST
                )

                titulo = (
                    f"Prévia — Modo normal · "
                    f"{percentual}%"
                )


            # ==================================================
            # MODO COMPACTO
            # Repete a mesma regra usada pelo carregador real:
            # crop comum + limite de 92x64.
            # ==================================================

            elif modo == "compact":

                pasta = (
                    base
                    / "compact"
                )

                arquivos = [
                    pasta / "01.png",
                    pasta / "02.png",
                    pasta / "03.png",
                ]

                imagens = []

                for arquivo in arquivos:
                    if arquivo.exists():
                        imagens.append(
                            Image.open(
                                arquivo
                            ).convert("RGBA")
                        )

                if not imagens:
                    raise FileNotFoundError(
                        pasta
                    )

                caixas = []

                for img in imagens:
                    bbox = (
                        img
                        .getchannel("A")
                        .getbbox()
                    )

                    if bbox:
                        caixas.append(
                            bbox
                        )

                if not caixas:
                    return

                left = min(
                    b[0]
                    for b in caixas
                )

                top = min(
                    b[1]
                    for b in caixas
                )

                right = max(
                    b[2]
                    for b in caixas
                )

                bottom = max(
                    b[3]
                    for b in caixas
                )

                crop_box = (
                    left,
                    top,
                    right,
                    bottom
                )

                largura = (
                    right
                    - left
                )

                altura = (
                    bottom
                    - top
                )

                escala_config = (
                    percentual
                    / 100.0
                )

                max_w = max(
                    1,
                    int(
                        92
                        * escala_config
                    )
                )

                max_h = max(
                    1,
                    int(
                        64
                        * escala_config
                    )
                )

                escala = min(
                    max_w / largura,
                    max_h / altura
                )

                novo_w = max(
                    1,
                    int(
                        largura
                        * escala
                    )
                )

                novo_h = max(
                    1,
                    int(
                        altura
                        * escala
                    )
                )

                imagem = (
                    imagens[0]
                    .crop(crop_box)
                    .resize(
                        (
                            novo_w,
                            novo_h
                        ),
                        Image.Resampling.NEAREST
                    )
                )

                titulo = (
                    f"Prévia — Modo compacto · "
                    f"{percentual}%"
                )

            else:
                return


            # ==================================================
            # MOSTRA A IMAGEM
            # ==================================================

            self._size_preview_photo = (
                ImageTk.PhotoImage(
                    imagem,
                    master=self.win
                )
            )

            self.size_preview_image_label.configure(
                image=self._size_preview_photo,
                text=""
            )

            self.size_preview_title.configure(
                text=titulo
            )

        except Exception as exc:

            self._size_preview_photo = None

            self.size_preview_image_label.configure(
                image=None,
                text="Não foi possível carregar a prévia."
            )

            self.size_preview_title.configure(
                text="Prévia"
            )

            print(
                "[MARVIN] Erro na previa de tamanho: "
                f"{exc}"
            )


    def _size_normal_changed(
        self,
        value,
        badge
    ):
        # Segunda camada da trava:
        # impede alteracoes por scroll ou qualquer outro evento
        # enquanto "Editar tamanho" estiver desmarcado.
        if not bool(self.v_edit_size.get()):
            atual = int(
                self.cfg.get(
                    "tamanho_normal",
                    self.v_size_normal.get()
                )
            )

            self.v_size_normal.set(
                atual
            )

            badge.configure(
                text=str(atual)
            )

            return

        value = int(
            round(float(value) / 5) * 5
        )

        badge.configure(
            text=str(value)
        )

        self._preview_size(
            "tamanho_normal",
            value
        )

        self._update_size_preview(
            "normal",
            value
        )

    def _size_compact_changed(
        self,
        value,
        badge
    ):
        if not bool(self.v_edit_size.get()):
            atual = int(
                self.cfg.get(
                    "tamanho_compacto",
                    self.v_size_compact.get()
                )
            )

            self.v_size_compact.set(
                atual
            )

            badge.configure(
                text=str(atual)
            )

            return

        value = int(
            round(float(value) / 5) * 5
        )

        badge.configure(
            text=str(value)
        )

        self._preview_size(
            "tamanho_compacto",
            value
        )

        self._update_size_preview(
            "compact",
            value
        )

    def _opacity_changed(
        self,
        value,
        badge
    ):
        if not bool(self.v_edit_size.get()):
            atual = float(
                self.cfg.get(
                    "opacidade",
                    self.v_op.get()
                )
            )

            self.v_op.set(
                atual
            )

            badge.configure(
                text=f"{atual:.2f}"
            )

            return

        value = round(
            float(value),
            2
        )

        badge.configure(
            text=f"{value:.2f}"
        )

        self._preview_opacity(
            value
        )

    # ==========================================================
    # INTERFACE
    # ==========================================================

    def _build(self):

        shell = ctk.CTkFrame(
            self.win,
            fg_color=self.colors["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"]
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        shell.grid_columnconfigure(
            0,
            weight=1
        )

        shell.grid_rowconfigure(
            2,
            weight=1
        )

        # ------------------------------------------------------
        # TITLEBAR
        # ------------------------------------------------------

        titlebar = ctk.CTkFrame(
            shell,
            height=48,
            corner_radius=0,
            fg_color="transparent"
        )

        titlebar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(4, 0)
        )

        titlebar.pack_propagate(False)

        mark = ctk.CTkLabel(
            titlebar,
            text="",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
                weight="bold"
            )
        )

        mark.pack(
            side="left",
            padx=(5, 8)
        )

        titulo = ctk.CTkLabel(
            titlebar,
            text="MARVIN — CONFIGURAÇÕES",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            )
        )

        titulo.pack(
            side="left"
        )

        fechar = ctk.CTkButton(
            titlebar,
            text="×",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["surface"],
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20
            ),
            command=self.win.destroy
        )

        fechar.pack(
            side="right"
        )

        for widget in (
            titlebar,
            mark,
            titulo
        ):
            widget.bind(
                "<ButtonPress-1>",
                self._drag_start
            )

            widget.bind(
                "<B1-Motion>",
                self._drag_move
            )

        ctk.CTkFrame(
            shell,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).grid(
            row=1,
            column=0,
            sticky="ew"
        )

        # ------------------------------------------------------
        # CONTEUDO
        # ------------------------------------------------------

        body = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["dim"]
        )

        # Usado para redirecionar a roda do mouse dos sliders
        # para a rolagem vertical das Configuracoes.
        self._settings_scroll = body

        body.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(18, 8),
            pady=(14, 4)
        )

        ctk.CTkLabel(
            body,
            text="Configurações",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=21,
                weight="bold"
            )
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            body,
            text="Personalize a aparência e o comportamento do MARVIN.",
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        ).pack(
            fill="x",
            pady=(2, 2)
        )

        # ======================================================
        # APARENCIA
        # ======================================================

        self._section_title(
            body,
            "Aparência"
        )

        self.v_tema = tk.StringVar(
            value=self.cfg.get(
                "tema",
                "escuro"
            )
        )

        tema_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        tema_card.pack(
            fill="x"
        )

        self.theme_selector = ctk.CTkSegmentedButton(
            tema_card,
            values=[
                "Escuro",
                "Claro"
            ],
            height=36,
            fg_color=self.colors["surface"],
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["surface"],
            unselected_hover_color=self.colors["border"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=self._tema_visual_changed
        )

        self.theme_selector.pack(
            fill="x",
            padx=4,
            pady=4
        )

        if self.v_tema.get() == "claro":
            self.theme_selector.set(
                "Claro"
            )
        else:
            self.theme_selector.set(
                "Escuro"
            )

        # ======================================================
        # COMPORTAMENTO
        # ======================================================

        self._section_title(
            body,
            "Comportamento"
        )

        self.v_som = tk.BooleanVar(
            value=self.cfg.get(
                "som",
                True
            )
        )

        self.v_startup = tk.BooleanVar(
            value=self._startup_enabled()
        )

        behavior_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        behavior_card.pack(
            fill="x"
        )

        self._toggle_row(
            behavior_card,
            "Som ao receber lembrete",
            "Toca um aviso quando uma tarefa chegar.",
            self.v_som
        )

        ctk.CTkFrame(
            behavior_card,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).pack(
            fill="x",
            padx=12
        )

        self._toggle_row(
            behavior_card,
            "Iniciar com o Windows",
            "Abre o MARVIN automaticamente ao entrar.",
            self.v_startup
        )

        # ======================================================
        # TAMANHO
        # ======================================================

        self._section_title(
            body,
            "Tamanho e exibição"
        )

        self.v_size_normal = tk.IntVar(
            value=self.cfg.get(
                "tamanho_normal",
                100
            )
        )

        self.v_size_compact = tk.IntVar(
            value=self.cfg.get(
                "tamanho_compacto",
                85
            )
        )

        self.v_op = tk.DoubleVar(
            value=self.cfg.get(
                "opacidade",
                1.0
            )
        )


        # ------------------------------------------------------
        # PROTECAO DOS CONTROLES DE TAMANHO
        # ------------------------------------------------------

        self.v_edit_size = tk.BooleanVar(
            value=False
        )

        self.edit_size_check = ctk.CTkCheckBox(
            body,
            text="Editar tamanho",
            variable=self.v_edit_size,
            onvalue=True,
            offvalue=False,
            command=self._toggle_size_edit,
            height=26,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            border_width=1,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            border_color=self.colors["border"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            )
        )

        self.edit_size_check.pack(
            fill="x",
            pady=(0, 12)
        )

        self.size_normal_slider = self._slider_block(
            body,
            "Tamanho do MARVIN",
            self.v_size_normal,
            60,
            120,
            12,
            str(self.v_size_normal.get()),
            self._size_normal_changed
        )

        self.size_compact_slider = self._slider_block(
            body,
            "Modo compacto",
            self.v_size_compact,
            60,
            120,
            12,
            str(self.v_size_compact.get()),
            self._size_compact_changed
        )

        # ------------------------------------------------------
        # PREVIA DE TAMANHO
        # ------------------------------------------------------

        self.size_preview_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"]
        )

        self.size_preview_card.pack(
            fill="x",
            pady=(12, 6)
        )

        self.size_preview_title = ctk.CTkLabel(
            self.size_preview_card,
            text="Prévia — ajuste um tamanho",
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold"
            )
        )

        self.size_preview_title.pack(
            fill="x",
            padx=14,
            pady=(10, 4)
        )

        self.size_preview_area = ctk.CTkFrame(
            self.size_preview_card,
            height=210,
            fg_color=self.colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )

        self.size_preview_area.pack(
            fill="x",
            padx=12,
            pady=(4, 12)
        )

        self.size_preview_area.pack_propagate(
            False
        )

        self.size_preview_image_label = ctk.CTkLabel(
            self.size_preview_area,
            text=(
                "Mova um dos controles de tamanho "
                "para visualizar."
            ),
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        )

        self.size_preview_image_label.pack(
            expand=True
        )

        self._size_preview_photo = None

        self.opacity_slider = self._slider_block(
            body,
            "Opacidade",
            self.v_op,
            0.3,
            1.0,
            14,
            f"{self.v_op.get():.2f}",
            self._opacity_changed
        )

        # Os tres controles ja existem neste ponto.
        # Aplicamos a trava somente agora.
        self._toggle_size_edit()

        # ======================================================
        # FRASES
        # ======================================================

        self._section_title(
            body,
            "Frases do MARVIN"
        )

        ctk.CTkLabel(
            body,
            text=(
                "Uma frase por linha. "
                "O MARVIN escolhe uma aleatoriamente."
            ),
            text_color=self.colors["dim"],
            anchor="w",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10
            )
        ).pack(
            fill="x",
            pady=(0, 6)
        )

        self.txt_frases = ctk.CTkTextbox(
            body,
            height=92,
            corner_radius=9,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            ),
            wrap="word"
        )

        self.txt_frases.pack(
            fill="x"
        )


        ctk.CTkLabel(
            body,
            text="Frequ\u00eancia das falas",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
        ).pack(
            fill="x",
            pady=(14, 3),
        )


        ctk.CTkLabel(
            body,
            text=(
                "Define com que frequ\u00eancia "
                "o Marvin fala sozinho."
            ),
            anchor="w",
            text_color=self.colors["dim"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),
        ).pack(
            fill="x",
            pady=(0, 6),
        )


        self.v_idle_frequency = tk.StringVar(
            value=self._idle_frequency_label(
                self.cfg.get(
                    "idle_interval_seconds",
                    300,
                )
            )
        )


        self.idle_frequency_menu = (
            ctk.CTkOptionMenu(
                body,
                values=list(
                    self._idle_frequency_options.keys()
                ),
                variable=self.v_idle_frequency,
                height=34,
                corner_radius=8,
                fg_color=self.colors["surface"],
                button_color=self.colors["accent"],
                button_hover_color=self.colors[
                    "accent_hover"
                ],
                text_color=self.colors["text"],
                dropdown_fg_color=self.colors[
                    "surface"
                ],
                dropdown_text_color=self.colors[
                    "text"
                ],
                dropdown_hover_color=self.colors[
                    "accent_hover"
                ],
            )
        )

        self.idle_frequency_menu.pack(
            fill="x",
            pady=(0, 4),
        )

        frases_atuais = self.cfg.get(
            "frases_idle",
            self._idle_msgs
        )

        if not isinstance(
            frases_atuais,
            list
        ):
            frases_atuais = self._idle_msgs

        self.txt_frases.insert(
            "1.0",
            "\n".join(
                frases_atuais
            )
        )

        ctk.CTkButton(
            body,
            text="Personalizar frases de espera",
            height=36,
            corner_radius=8,
            fg_color=self.colors["surface"],
            hover_color=self.colors["border"],
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["accent"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=lambda: self._waiting_phrases_factory(
                self.win,
                self.comp
            )
        ).pack(
            fill="x",
            pady=(8, 0)
        )

        # ======================================================
        # DADOS
        # ======================================================

        self._section_title(
            body,
            "Dados"
        )

        ctk.CTkButton(
            body,
            text="Limpar tarefas concluídas há mais de 30 dias",
            height=38,
            corner_radius=8,
            fg_color=self.colors["danger_bg"],
            hover_color=self.colors["border"],
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["danger_fg"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=self._limpar
        ).pack(
            fill="x"
        )

        db_box = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )

        db_box.pack(
            fill="x",
            pady=(8, 18)
        )

        ctk.CTkLabel(
            db_box,
            text=f"DB: {self._db_path}",
            text_color=self.colors["dim"],
            anchor="w",
            justify="left",
            wraplength=350,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9
            )
        ).pack(
            fill="x",
            padx=10,
            pady=8
        )

        # ======================================================
        # FOOTER
        # ======================================================

        footer = ctk.CTkFrame(
            shell,
            fg_color=self.colors["card"],
            corner_radius=0
        )

        footer.grid(
            row=3,
            column=0,
            sticky="ew"
        )

        ctk.CTkFrame(
            footer,
            height=1,
            corner_radius=0,
            fg_color=self.colors["border"]
        ).pack(
            fill="x"
        )

        ctk.CTkButton(
            footer,
            text="Salvar alterações",
            height=42,
            corner_radius=9,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            command=self._salvar
        ).pack(
            fill="x",
            padx=18,
            pady=12
        )

    # ==========================================================
    # SCROLL
    # ==========================================================

    def _scroll_settings_from_control(
        self,
        event
    ):
        """
        Faz a roda do mouse sobre os sliders se comportar
        exatamente como a rolagem normal das Configuracoes.
        """

        try:
            canvas = getattr(
                self._settings_scroll,
                "_parent_canvas",
                None
            )

            if canvas is None:
                return "break"

            delta = getattr(
                event,
                "delta",
                0
            )

            if not delta:
                return "break"

            # Mesma formula usada internamente pelo
            # CTkScrollableFrame no Windows.
            unidades = -int(
                delta / 6
            )

            if unidades:
                canvas.yview(
                    "scroll",
                    unidades,
                    "units"
                )

        except Exception:
            pass

        return "break"

    # ==========================================================
    # PREVIEWS
    # ==========================================================

    def _preview_size(self, chave, valor):
        try:
            valor = int(float(valor))
        except (TypeError, ValueError):
            return

        self.cfg[chave] = valor
        save_cfg(self.cfg)

        try:
            self.comp._reload_sprites()
        except Exception as exc:
            print(
                f"[MARVIN] Erro ao atualizar tamanho: {exc}"
            )

    def _preview_opacity(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return

        valor = max(
            0.3,
            min(1.0, valor)
        )

        self.cfg["opacidade"] = round(
            valor,
            2
        )

        save_cfg(self.cfg)

        try:
            self.comp.root.attributes(
                "-alpha",
                valor
            )
        except Exception as exc:
            print(
                f"[MARVIN] Erro ao alterar opacidade: {exc}"
            )

    # ==========================================================
    # SALVAR
    # ==========================================================

    def _salvar(self):
        tema_anterior = self.cfg.get(
            "tema",
            "escuro"
        )

        self.cfg["tema"] = self.v_tema.get()

        self.cfg["som"] = self.v_som.get()

        self.cfg["opacidade"] = round(
            self.v_op.get(),
            2
        )

        self.cfg["tamanho_normal"] = int(
            self.v_size_normal.get()
        )

        self.cfg["tamanho_compacto"] = int(
            self.v_size_compact.get()
        )

        frases = [
            linha.strip()
            for linha in self.txt_frases.get(
                "1.0",
                "end"
            ).splitlines()
            if linha.strip()
        ]

        self.cfg["frases_idle"] = (
            frases
            if frases
            else list(self._idle_msgs)
        )

        self.cfg["idle_interval_seconds"] = (
            self._idle_frequency_options.get(
                self.v_idle_frequency.get(),
                300,
            )
        )

        save_cfg(self.cfg)

        # Aplica a nova frequencia imediatamente.
        try:
            self.comp._schedule_idle()
        except Exception:
            pass


        tema_mudou = (
            tema_anterior
            != self.cfg["tema"]
        )

        startup_ok = self._set_startup_enabled(
            self.v_startup.get()
        )

        if not startup_ok:
            messagebox.showwarning(
                "MARVIN",
                "Nao foi possivel alterar a inicializacao com o Windows."
            )

        self.comp._reload_sprites()

        try:
            self.comp.root.attributes(
                "-alpha",
                self.cfg["opacidade"]
            )
        except Exception:
            pass

        if tema_mudou:
            self.win.destroy()

            # Para explicitamente o icone antigo da bandeja
            # antes de substituir o processo.
            tray_icon = getattr(
                self.comp,
                "_tray_icon",
                None
            )

            if tray_icon is not None:
                try:
                    tray_icon.stop()
                except Exception:
                    pass
                finally:
                    self.comp._tray_icon = None

            os.execl(
                sys.executable,
                sys.executable,
                "-m",
                "marvin.main",
            )

            return

        self.comp.say(
            "Configuracoes salvas!",
            "talking",
            2500
        )

        self.win.destroy()

    def _limpar(self):
        self._db_cleaner(30)

        self.comp.say(
            "Limpeza concluida!",
            "talking",
            2500
        )

        self.win.destroy()
