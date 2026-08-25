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