DARK = {
    "win_bg": "#0F1115",
    "panel": "#171A20",
    "border": "#292D35",
    "text": "#F4F5F7",
    "dim": "#8B929D",
    "accent": "#6695FF",
    "green": "#48B978",
    "red": "#E5636C",
    "orange": "#D59A45",
    "purple": "#A58AF0",
    "bub_bg": "#171A20",
    "bub_bd": "#6695FF",
}


LIGHT = {
    "win_bg": "#F6F7F9",
    "panel": "#FFFFFF",
    "border": "#E2E5E9",
    "text": "#17191C",
    "dim": "#747B86",
    "accent": "#356AE6",
    "green": "#238A57",
    "red": "#D34552",
    "orange": "#AD7627",
    "purple": "#7656C9",
    "bub_bg": "#FFFFFF",
    "bub_bd": "#356AE6",
}


def get_palette(tema):
    if str(tema).lower() == "claro":
        return dict(LIGHT)

    return dict(DARK)

# ============================================================
# INTERFACE MODERNA
# ============================================================

_MODERN_PALETTES = {

    "task_form": {

        "claro": {
            "bg": "#F9F8F6",
            "card": "#FFFFFF",
            "text": "#2C2C2A",
            "dim": "#888780",
            "border": "#E3E1DC",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "input": "#FFFFFF",
            "input_hover": "#F6F4EF",

            "high_bg": "#FAE7E5",
            "high_fg": "#A33A32",

            "normal_bg": "#FFF0D9",
            "normal_fg": "#9A6424",

            "low_bg": "#E7F3EA",
            "low_fg": "#39734A",

            "none_bg": "#F1EFE8",
            "none_fg": "#6F6D67",

            "error": "#C54B45",
        },

        "escuro": {
            "bg": "#1A1915",
            "card": "#232220",
            "text": "#EFEDE8",
            "dim": "#85837D",
            "border": "#34332F",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "input": "#232220",
            "input_hover": "#2C2B28",

            "high_bg": "#482522",
            "high_fg": "#F19A91",

            "normal_bg": "#49351F",
            "normal_fg": "#E8B86D",

            "low_bg": "#20382A",
            "low_fg": "#83C995",

            "none_bg": "#2C2C2A",
            "none_fg": "#B4B2A9",

            "error": "#F08078",
        },
    },

    "task_list": {

        "claro": {
            "bg": "#F9F8F6",
            "card": "#FFFFFF",
            "text": "#2C2C2A",
            "dim": "#888780",
            "border": "#E3E1DC",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "hover": "#F1EFE8",

            "high_bg": "#FAE7E5",
            "high_fg": "#A33A32",

            "medium_bg": "#FFF0D9",
            "medium_fg": "#9A6424",

            "low_bg": "#E7F3EA",
            "low_fg": "#39734A",

            "none_bg": "#F1EFE8",
            "none_fg": "#6F6D67",

            "done_bg": "#E1F5EE",
            "done_fg": "#238A57",

            "red": "#C54B45",
        },

        "escuro": {
            "bg": "#1A1915",
            "card": "#232220",
            "text": "#EFEDE8",
            "dim": "#85837D",
            "border": "#34332F",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "hover": "#2C2B28",

            "high_bg": "#482522",
            "high_fg": "#F19A91",

            "medium_bg": "#49351F",
            "medium_fg": "#E8B86D",

            "low_bg": "#20382A",
            "low_fg": "#83C995",

            "none_bg": "#2C2C2A",
            "none_fg": "#B4B2A9",

            "done_bg": "#04342C",
            "done_fg": "#5DCAA5",

            "red": "#F08078",
        },
    },

    "settings": {

        "claro": {
            "bg": "#F9F8F6",
            "card": "#FFFFFF",
            "surface": "#F3F1ED",
            "text": "#2C2C2A",
            "dim": "#888780",
            "border": "#E3E1DC",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "danger_bg": "#FFF0E8",
            "danger_fg": "#A85638",
        },

        "escuro": {
            "bg": "#1A1915",
            "card": "#232220",
            "surface": "#2C2B28",
            "text": "#EFEDE8",
            "dim": "#AAA79F",
            "border": "#3B3935",

            "accent": "#D97757",
            "accent_hover": "#E18868",

            "danger_bg": "#392820",
            "danger_fg": "#E6A082",
        },
    },

    "interaction": {

        "claro": {
            "bg": "#F9F8F6",
            "card": "#FFFFFF",
            "text": "#2C2C2A",
            "dim": "#888780",
            "border": "#E3E1DC",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "green": "#238A57",
            "green_bg": "#E1F5EE",

            "orange_bg": "#FAECE7",

            "hover": "#F1EFE8",
        },

        "escuro": {
            "bg": "#1A1915",
            "card": "#232220",
            "text": "#EFEDE8",
            "dim": "#85837D",
            "border": "#34332F",

            "accent": "#D97757",
            "accent_hover": "#C96844",

            "green": "#5DCAA5",
            "green_bg": "#04342C",

            "orange_bg": "#4A1B0C",

            "hover": "#2C2B28",
        },
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
