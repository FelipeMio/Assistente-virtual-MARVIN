import customtkinter as ctk

from marvin.config import load_cfg
from marvin.theme import get_modern_palette
from marvin.ui.branding import round_window, title_icon
from marvin.ui.window_position import position_near


# Acima disso a mensagem ganha rolagem, para o botao
# "Entendi" nunca ficar escondido atras da barra de tarefas.
MAX_TEXT_HEIGHT = 260


def _fonte(size, weight="normal"):
    return ctk.CTkFont(
        family="Segoe UI",
        size=size,
        weight=weight,
    )


class B2BAlertWindow:

    WIDTH = 400

    def __init__(
        self,
        comp,
        mensagem,
        on_entendi,
        restantes=0,
    ):
        self.comp = comp
        self.on_entendi = on_entendi

        tema = load_cfg().get("tema", "escuro")
        self.c = get_modern_palette(tema, "interaction")

        self.win = ctk.CTkToplevel(comp.root)

        # Fica invisivel ate estar no lugar certo.
        # Antes a janela aparecia por um instante
        # na posicao padrao do Windows.
        self.win.withdraw()

        self.win.title("MARVIN - Aviso B2B")
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        round_window(self.win, self.c)

        # O aviso so fecha pelo botao Entendi.
        self.win.protocol(
            "WM_DELETE_WINDOW",
            lambda: None,
        )

        self._drag = (0, 0)

        self._build(mensagem, restantes)

        self.win.after(
            30,
            self._posicionar,
        )

    # ========================================================
    # INTERFACE
    # ========================================================

    def _build(self, mensagem, restantes):
        shell = ctk.CTkFrame(
            self.win,
            width=self.WIDTH,
            fg_color=self.c["bg"],
            corner_radius=14,
            border_width=1,
            border_color=self.c["border"],
        )
        shell.pack(fill="both", expand=True, padx=1, pady=1)

        # Barra de titulo
        barra = ctk.CTkFrame(
            shell,
            height=44,
            fg_color="transparent",
        )
        # Pequena margem para nao cobrir a borda arredondada.
        barra.pack(fill="x", padx=2, pady=(2, 0))
        barra.pack_propagate(False)

        drag = (self._drag_start, self._drag_move)

        title_icon(barra, self.c, drag=drag)

        rotulo = ctk.CTkLabel(
            barra,
            text="AVISO B2B",
            text_color=self.c["dim"],
            font=_fonte(10, "bold"),
        )
        rotulo.pack(side="left", padx=(8, 0))

        if restantes:
            ctk.CTkLabel(
                barra,
                text=(
                    f"  +{restantes} na fila  "
                ),
                height=20,
                corner_radius=6,
                fg_color=self.c["orange_bg"],
                text_color=self.c["accent"],
                font=_fonte(9, "bold"),
            ).pack(side="right", padx=14)

        for widget in (barra, rotulo):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        ctk.CTkFrame(
            shell,
            height=1,
            fg_color=self.c["border"],
        ).pack(fill="x")

        # Rodape primeiro: assim ele sempre tem espaco,
        # mesmo quando a mensagem e muito longa.
        rodape = ctk.CTkFrame(shell, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=18, pady=(10, 16))

        ctk.CTkButton(
            rodape,
            text="Entendi",
            height=36,
            corner_radius=8,
            fg_color=self.c["accent"],
            hover_color=self.c["accent_hover"],
            text_color="#FFFFFF",
            font=_fonte(11, "bold"),
            command=self._entendi,
        ).pack(fill="x")

        corpo = ctk.CTkFrame(shell, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=18, pady=(14, 0))

        titulo, detalhes = self._separar(mensagem)

        ctk.CTkLabel(
            corpo,
            text=titulo,
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 40,
            text_color=self.c["text"],
            font=_fonte(12, "bold"),
        ).pack(fill="x")

        if detalhes:
            self._detalhes(corpo, detalhes)

    @staticmethod
    def _separar(mensagem):
        """Primeira linha vira titulo; o resto, detalhes."""
        partes = mensagem.strip().split("\n", 1)
        titulo = partes[0].strip()
        detalhes = partes[1].strip() if len(partes) > 1 else ""
        return titulo, detalhes

    def _detalhes(self, parent, detalhes):
        caixa = ctk.CTkTextbox(
            parent,
            width=self.WIDTH - 36,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.c["border"],
            fg_color=self.c["card"],
            text_color=self.c["text"],
            scrollbar_button_color=self.c["border"],
            scrollbar_button_hover_color=self.c["dim"],
            wrap="word",
            activate_scrollbars=True,
            font=_fonte(10),
        )
        caixa.pack(fill="both", expand=True, pady=(10, 0))

        caixa.insert("1.0", detalhes)
        caixa.configure(state="disabled")

        # Ajusta a altura ao conteudo, com limite.
        # (Com a janela escondida o Tk nao sabe contar as
        # linhas quebradas, entao a conta e feita pela fonte.)
        fonte = _fonte(10)
        largura_util = self.WIDTH - 36 - 40

        try:
            linha_px = fonte.metrics("linespace")
            linhas = sum(
                max(1, -(-fonte.measure(linha) // largura_util))
                for linha in detalhes.splitlines()
            )
        except Exception:
            linha_px = 15
            linhas = len(detalhes.splitlines()) or 1

        altura = min(
            MAX_TEXT_HEIGHT,
            # +1 linha e margem: espacamento interno da caixa.
            max(40, (linhas + 1) * linha_px + 22),
        )

        caixa.configure(height=altura)

    # ========================================================
    # POSICAO
    # ========================================================

    def _posicionar(self):
        try:
            self.win.update_idletasks()

            # position_near usa a area util do monitor
            # (sem a barra de tarefas) e mantem a janela
            # inteira visivel, ao lado do MARVIN.
            position_near(
                self.win,
                self.comp.root,
            )

        except Exception:
            self.win.geometry("+100+100")

        self.win.deiconify()
        self.win.lift()
        self.win.attributes("-topmost", True)

        try:
            self.win.focus_force()
        except Exception:
            pass

    def _drag_start(self, event):
        self._drag = (
            event.x_root - self.win.winfo_x(),
            event.y_root - self.win.winfo_y(),
        )

    def _drag_move(self, event):
        dx, dy = self._drag
        self.win.geometry(
            f"+{event.x_root - dx}+{event.y_root - dy}"
        )

    # ========================================================
    # ACOES
    # ========================================================

    def _entendi(self):
        try:
            self.win.destroy()
        except Exception:
            pass

        if callable(self.on_entendi):
            self.on_entendi()
