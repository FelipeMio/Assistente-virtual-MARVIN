# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all(
    "customtkinter"
)


a = Analysis(
    ["run_marvin.py"],

    pathex=[],

    binaries=ctk_binaries,

    datas=ctk_datas + [
        ("marvin/assets", "marvin/assets"),
        ("assets", "assets"),
    ],

    hiddenimports=ctk_hiddenimports,

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],

    noarchive=False,
    optimize=0,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,

    [],

    exclude_binaries=True,

    name="MARVIN",

    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,

    console=False,

    disable_windowed_traceback=False,
    argv_emulation=False,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,

    strip=False,
    upx=True,

    name="MARVIN",
)
