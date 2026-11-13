import pytest

from marvin.hotkey import (
    MOD_ALT,
    MOD_CONTROL,
    MOD_SHIFT,
    atalho_de_evento,
    parse_atalho,
)


CTRL = 0x4
ALT = 0x20000
SHIFT = 0x1
NUMLOCK = 0x8


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("Ctrl+Alt+M", (MOD_CONTROL | MOD_ALT, ord("M"))),
        ("ctrl+shift+f9", (MOD_CONTROL | MOD_SHIFT, 0x78)),
        ("Alt+Space", (MOD_ALT, 0x20)),
        ("Ctrl+Alt+7", (MOD_CONTROL | MOD_ALT, ord("7"))),
        ("M", None),
        ("Ctrl+Foo+M", None),
        ("Ctrl+Alt+F13", None),
    ],
)
def test_parse_atalho(texto, esperado):
    assert parse_atalho(texto) == esperado


@pytest.mark.parametrize(
    "keysym, state, esperado",
    [
        ("k", CTRL | ALT | NUMLOCK, "Ctrl+Alt+K"),
        ("K", CTRL | SHIFT | NUMLOCK, "Ctrl+Shift+K"),
        ("F9", CTRL | ALT, "Ctrl+Alt+F9"),
        ("space", CTRL, "Ctrl+Space"),
        ("n", ALT, "Alt+N"),
        ("Control_L", CTRL, None),
        ("Alt_L", ALT, None),
        ("k", SHIFT, ""),
        ("k", 0, ""),
        ("Return", CTRL, ""),
    ],
)
def test_atalho_de_evento(keysym, state, esperado):
    assert atalho_de_evento(keysym, state) == esperado
