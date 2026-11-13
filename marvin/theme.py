# ============================================================
# PALETA BASE
# ============================================================
#
# Todas as janelas partem das mesmas cores neutras e do
# mesmo destaque (laranja MARVIN). Cada perfil abaixo apenas
# acrescenta as cores especificas da sua janela.

ACCENT = "#D97757"

_BASE = {
    "claro": {
        "bg": "#F9F8F6",
        "card": "#FFFFFF",
        "surface": "#F3F1ED",
        "text": "#2C2C2A",
        "dim": "#7C7A73",
        "muted": "#A6A49D",
        "border": "#E3E1DC",
        "hover": "#F1EFE8",

        "accent": ACCENT,
        "accent_hover": "#C96844",
        "on_accent": "#FFFFFF",

        "green": "#238A57",
        "green_bg": "#E1F5EE",
        "red": "#C54B45",
    },

    "escuro": {
        "bg": "#1A1915",
        "card": "#232220",
        "surface": "#2C2B28",
        "text": "#EFEDE8",
        "dim": "#9C9990",
        "muted": "#5F5E5A",
        "border": "#34332F",
        "hover": "#2C2B28",

        "accent": ACCENT,
        "accent_hover": "#E18868",
        "on_accent": "#FFFFFF",

        "green": "#5DCAA5",
        "green_bg": "#04342C",
        "red": "#F08078",
    },
}


# Cores de prioridade compartilhadas por formulario e lista.
_PRIORITY = {
    "claro": {
        "high_bg": "#FAE7E5",
        "high_fg": "#A33A32",
        "medium_bg": "#FFF0D9",
        "medium_fg": "#9A6424",
        "low_bg": "#E7F3EA",
        "low_fg": "#39734A",
        "none_bg": "#F1EFE8",
        "none_fg": "#6F6D67",
    },

    "escuro": {
        "high_bg": "#482522",
        "high_fg": "#F19A91",
        "medium_bg": "#49351F",
        "medium_fg": "#E8B86D",
        "low_bg": "#20382A",
        "low_fg": "#83C995",
        "none_bg": "#2C2C2A",
        "none_fg": "#B4B2A9",
    },
}


def _legacy(tema):
    """Paleta usada pelo personagem e pelo balao de fala."""
    b = _BASE[tema]
    return {
        "win_bg": b["bg"],
        "panel": b["card"],
        "border": b["border"],
        "text": b["text"],
        "dim": b["dim"],
        "accent": b["accent"],
        "green": "#48B978" if tema == "escuro" else "#238A57",
        "red": "#E5636C" if tema == "escuro" else "#D34552",
        "orange": "#D59A45" if tema == "escuro" else "#AD7627",
        "purple": "#A58AF0" if tema == "escuro" else "#7656C9",
        "bub_bg": b["card"],
        "bub_bd": b["accent"],
    }


DARK = _legacy("escuro")
LIGHT = _legacy("claro")


def get_palette(tema):
    if str(tema).lower() == "claro":
        return dict(LIGHT)

    return dict(DARK)


# ============================================================
# PERFIS POR JANELA
# ============================================================

def _profile(tema, **extra):
    return {**_BASE[tema], **extra}


def _priority_form(tema):
    p = _PRIORITY[tema]
    return {
        "high_bg": p["high_bg"],
        "high_fg": p["high_fg"],
        "normal_bg": p["medium_bg"],
        "normal_fg": p["medium_fg"],
        "low_bg": p["low_bg"],
        "low_fg": p["low_fg"],
        "none_bg": p["none_bg"],
        "none_fg": p["none_fg"],
    }


_MODERN_PALETTES = {

    "task_form": {
        tema: _profile(
            tema,
            input=_BASE[tema]["card"],
            input_hover=_BASE[tema]["hover"],
            error=_BASE[tema]["red"],
            **_priority_form(tema),
        )
        for tema in _BASE
    },

    "task_list": {
        tema: _profile(
            tema,
            done_bg="#E1F5EE" if tema == "claro" else "#04342C",
            done_fg="#238A57" if tema == "claro" else "#5DCAA5",
            **_PRIORITY[tema],
        )
        for tema in _BASE
    },

    "settings": {
        "claro": _profile(
            "claro",
            danger_bg="#FFF0E8",
            danger_fg="#A85638",
        ),
        "escuro": _profile(
            "escuro",
            danger_bg="#392820",
            danger_fg="#E6A082",
        ),
    },

    "home": {
        "claro": _profile(
            "claro",
            button_hover=_BASE["claro"]["hover"],
            tasks_bg="#EEEDFE",
            tasks_fg="#534AB7",
            check_bg="#E1F5EE",
            check_fg="#0F6E56",
            summary_bg="#F1EFE8",
            summary_fg="#5F5E5A",
            ext_bg="#FAECE7",
            ext_fg="#993C1D",
        ),
        "escuro": _profile(
            "escuro",
            button_hover=_BASE["escuro"]["hover"],
            tasks_bg="#26215C",
            tasks_fg="#AFA9EC",
            check_bg="#04342C",
            check_fg="#5DCAA5",
            summary_bg="#2C2C2A",
            summary_fg="#B4B2A9",
            ext_bg="#4A1B0C",
            ext_fg="#F0997B",
        ),
    },

    "interaction": {
        "claro": _profile("claro", orange_bg="#FAECE7"),
        "escuro": _profile("escuro", orange_bg="#4A1B0C"),
    },

    # Checklist diario e outras janelas simples.
    "checklist": {
        tema: _profile(
            tema,
            done_bg="#E1F5EE" if tema == "claro" else "#04342C",
            done_fg="#238A57" if tema == "claro" else "#5DCAA5",
        )
        for tema in _BASE
    },
}


def get_modern_palette(tema, profile):

    if profile not in _MODERN_PALETTES:
        raise ValueError(
            f"Perfil de paleta desconhecido: {profile}"
        )

    tema = (
        "claro"
        if tema == "claro"
        else "escuro"
    )

    return dict(
        _MODERN_PALETTES[profile][tema]
    )
