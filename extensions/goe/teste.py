import sys
from pathlib import Path


COMANDOS = {
    "parado",
    "normal",
    "ok",
}


def main():
    if len(sys.argv) != 2:
        print("Uso:")
        print("  python extensions\\goe\\teste.py parado")
        print("  python extensions\\goe\\teste.py normal")
        print("  python extensions\\goe\\teste.py ok")
        raise SystemExit(1)

    comando = sys.argv[1].lower().strip()

    if comando not in COMANDOS:
        print(f"Comando invalido: {comando}")
        raise SystemExit(1)

    arquivo = (
        Path(__file__).resolve().parent
        / ".goe_test_command"
    )

    arquivo.write_text(
        comando,
        encoding="utf-8"
    )

    print(
        f"[GOE TESTE] comando enviado: {comando}"
    )


if __name__ == "__main__":
    main()
