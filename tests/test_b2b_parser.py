import importlib.util
from pathlib import Path


def _load_parser():
    parser_path = (
        Path(__file__)
        .resolve()
        .parents[1]
        / "extensions"
        / "b2b_telegram"
        / "parser.py"
    )

    spec = (
        importlib.util
        .spec_from_file_location(
            "marvin_b2b_parser_test",
            parser_path,
        )
    )

    assert spec is not None
    assert spec.loader is not None

    module = (
        importlib.util
        .module_from_spec(spec)
    )

    spec.loader.exec_module(
        module
    )

    return module


def test_extract_files():
    parser = _load_parser()

    text = (
        "Novos arquivos encontrados:\n"
        "\U0001f4c1 \u2500\u2500 Pasta Financeiro\n"
        "\U0001f4c4 \u2500\u2500 relatorio.csv\n"
        "\U0001f4c1 \u2500\u2500 Pasta Clientes\n"
        "\U0001f4c4 \u2500\u2500 clientes.xlsx"
    )

    result = parser.extrair_arquivos(
        text
    )

    assert result == [
        {
            "pasta": "Pasta Financeiro",
            "arquivo": "relatorio.csv",
        },
        {
            "pasta": "Pasta Clientes",
            "arquivo": "clientes.xlsx",
        },
    ]


def test_invalid_header_returns_empty():
    parser = _load_parser()

    result = parser.extrair_arquivos(
        "Mensagem comum\narquivo.csv"
    )

    assert result == []


def test_non_string_returns_empty():
    parser = _load_parser()

    assert (
        parser.extrair_arquivos(None)
        == []
    )
