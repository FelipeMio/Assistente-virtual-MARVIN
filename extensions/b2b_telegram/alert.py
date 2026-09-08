import tkinter as tk


class B2BAlertWindow:

    def __init__(
        self,
        comp,
        mensagem,
        on_entendi,
    ):
        self.comp = comp
        self.on_entendi = on_entendi

        self.win = tk.Toplevel(comp.root)

        self.win.title(
            "MARVIN - Aviso B2B"
        )

        self.win.attributes(
            "-topmost",
            True,
        )

        self.win.resizable(
            False,
            False,
        )

        self.win.configure(
            bg="#171717"
        )

        # O aviso so fecha pelo botao Entendi.
        self.win.protocol(
            "WM_DELETE_WINDOW",
            lambda: None,
        )

        titulo = tk.Label(
            self.win,
            text="Novo aviso B2B",
            bg="#171717",
            fg="#ffffff",
            font=("Segoe UI", 14, "bold"),
        )

        titulo.pack(
            padx=28,
            pady=(22, 10),
        )

        self.label = tk.Label(
            self.win,
            text=mensagem,
            bg="#171717",
            fg="#dddddd",
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
            wraplength=380,
        )

        self.label.pack(
            padx=28,
            pady=(0, 20),
        )

        botao = tk.Button(
            self.win,
            text="Entendi",
            command=self._entendi,
            bg="#D97757",
            fg="#ffffff",
            activebackground="#C86A4D",
            activeforeground="#ffffff",
            bd=0,
            padx=30,
            pady=9,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )

        botao.pack(
            pady=(0, 22),
        )

        self.win.after(
            50,
            self._posicionar,
        )

    def _posicionar(self):
        self.win.update_idletasks()

        largura = self.win.winfo_reqwidth()
        altura = self.win.winfo_reqheight()

        try:
            x = (
                self.comp.root.winfo_x()
                - largura
                - 15
            )

            y = self.comp.root.winfo_y()

        except Exception:
            x = 100
            y = 100

        self.win.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        self.win.lift()
        self.win.focus_force()

    def _entendi(self):
        try:
            self.win.destroy()
        except Exception:
            pass

        if callable(self.on_entendi):
            self.on_entendi()
