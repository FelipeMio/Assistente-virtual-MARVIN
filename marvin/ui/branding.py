"""Elementos visuais compartilhados pelas janelas do MARVIN."""

from pathlib import Path

import customtkinter as ctk


ICON_PATH = (
    Path(__file__).resolve().parents[2]
    / "assets"
    / "marvin"
    / "marvin_head.png"
)

_cache = {}


def marvin_icon(size=20):
    """Retorna o rosto do MARVIN como CTkImage (erro se o PNG faltar)."""
    if size in _cache:
        return _cache[size]

    from PIL import Image

    imagem = Image.open(ICON_PATH).convert("RGBA")

    # O PNG tem bastante margem transparente: recorta o
    # personagem e reduz sem suavizar, mantendo o pixel art nitido.
    bbox = imagem.getchannel("A").getbbox()

    if bbox:
        imagem = imagem.crop(bbox)

    # O recorte nao e quadrado: centraliza num quadrado transparente
    # para nao esticar o personagem ao redimensionar.
    lado = max(imagem.size)
    quadrado = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    quadrado.paste(
        imagem,
        ((lado - imagem.width) // 2, (lado - imagem.height) // 2),
    )

    imagem = quadrado.resize((size, size), Image.NEAREST)

    icon = ctk.CTkImage(
        light_image=imagem,
        dark_image=imagem,
        size=(size, size),
    )

    _cache[size] = icon
    return icon


def title_icon(parent, colors, *, size=20, padx=(14, 0), drag=None):
    """
    Coloca o rosto do MARVIN no canto esquerdo da barra de titulo.

    drag: tupla opcional (inicio, movimento) para permitir arrastar
    a janela tambem clicando no icone.
    """
    try:
        icon = marvin_icon(size)
    except Exception:
        icon = None

    if icon is not None:
        label = ctk.CTkLabel(
            parent,
            text="",
            image=icon,
            width=size,
            height=size,
        )

    else:
        label = ctk.CTkLabel(
            parent,
            text="M",
            width=size,
            height=size,
            corner_radius=6,
            fg_color=colors["accent"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
        )

    label.pack(side="left", padx=padx)

    if drag:
        label.bind("<ButtonPress-1>", drag[0])
        label.bind("<B1-Motion>", drag[1])

    return label


def title_text(parent, colors, text, *, drag=None):
    """Nome da janela na barra de titulo, no padrao do app."""
    label = ctk.CTkLabel(
        parent,
        text=text.upper(),
        text_color=colors["dim"],
        font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
    )
    label.pack(side="left", padx=(8, 0))

    if drag:
        label.bind("<ButtonPress-1>", drag[0])
        label.bind("<B1-Motion>", drag[1])

    return label


def close_button(parent, colors, command, *, hover=None):
    """Botao de fechar (x) no padrao do app."""
    button = ctk.CTkButton(
        parent,
        text="×",
        width=28,
        height=28,
        corner_radius=7,
        fg_color="transparent",
        hover_color=hover or colors.get("hover") or colors["border"],
        text_color=colors["dim"],
        font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
        command=command,
    )
    button.pack(side="right", padx=10)
    return button
