import importlib.util
import logging
import sys
from pathlib import Path


logger = logging.getLogger(
    "marvin.extensions"
)


def carregar_extensoes(companion):
    """
    Procura extensoes na pasta /extensions.

    Cada extensao deve possuir:
        extensions/NOME/__init__.py

    E expor:
        iniciar_extensao(companion)
    """

    raiz = (
        Path(__file__).resolve().parent.parent
        / "extensions"
    )

    if not raiz.exists():
        return []

    carregadas = []

    for pasta in sorted(raiz.iterdir()):
        if not pasta.is_dir():
            continue

        if pasta.name.startswith((".", "_")):
            continue

        init_file = pasta / "__init__.py"

        if not init_file.exists():
            continue

        nome_modulo = f"marvin_ext_{pasta.name}"

        try:
            spec = importlib.util.spec_from_file_location(
                nome_modulo,
                init_file,
                submodule_search_locations=[str(pasta)],
            )

            if spec is None or spec.loader is None:
                continue

            modulo = importlib.util.module_from_spec(spec)

            sys.modules[nome_modulo] = modulo

            spec.loader.exec_module(modulo)

            iniciar = getattr(
                modulo,
                "iniciar_extensao",
                None,
            )

            if not callable(iniciar):
                logger.warning(
                    "Extensao '%s' nao possui "
                    "iniciar_extensao().",
                    pasta.name,
                )
                continue

            objetos = iniciar(companion)

            if objetos:
                if isinstance(
                    objetos,
                    (list, tuple, set),
                ):
                    carregadas.extend(objetos)
                else:
                    carregadas.append(objetos)

            logger.info(
                "Extensao carregada: %s",
                pasta.name,
            )

        except Exception:
            logger.exception(
                "Erro na extensao '%s'.",
                pasta.name,
            )

    return carregadas
