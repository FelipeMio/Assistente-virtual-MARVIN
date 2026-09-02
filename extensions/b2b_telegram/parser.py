import re


HEADER = "Novos arquivos encontrados:"


def _limpar_decoracao(linha):
    """
    Remove emojis e simbolos colocados
    antes do nome da pasta ou arquivo.
    """
    linha = linha.strip()

    if "──" in linha:
        linha = linha.split("──", 1)[1]

    linha = re.sub(
        r"^[^\wÀ-ÿ.\-]+",
        "",
        linha,
    )

    return linha.strip()


def extrair_arquivos(texto):
    """
    Extrai pares de pasta e arquivo
    das mensagens do monitor B2B.
    """

    if not isinstance(texto, str):
        return []

    linhas = [
        linha.strip()
        for linha in texto.splitlines()
        if linha.strip()
    ]

    if not linhas:
        return []

    if HEADER not in linhas[0]:
        return []

    conteudo = linhas[1:]
    arquivos = []

    # O bot envia sempre:
    # pasta
    # arquivo
    # pasta
    # arquivo...
    for indice in range(0, len(conteudo) - 1, 2):

        pasta = _limpar_decoracao(
            conteudo[indice]
        )

        arquivo = _limpar_decoracao(
            conteudo[indice + 1]
        )

        if not arquivo:
            continue

        arquivos.append(
            {
                "pasta": pasta or None,
                "arquivo": arquivo,
            }
        )

    return arquivos
