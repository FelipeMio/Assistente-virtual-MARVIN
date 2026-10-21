import logging
import os
import sys

from logging.handlers import RotatingFileHandler
from pathlib import Path


LOGGER_NAME = "marvin"

DEFAULT_LEVEL = logging.INFO
DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_BACKUP_COUNT = 3


def _resolve_level(
    value=None,
):
    if value is None:
        value = os.getenv(
            "MARVIN_LOG_LEVEL",
            "INFO",
        )

    if isinstance(
        value,
        int,
    ):
        return value

    level = getattr(
        logging,
        str(value).upper(),
        None,
    )

    if not isinstance(
        level,
        int,
    ):
        return DEFAULT_LEVEL

    return level


def get_log_dir(
    log_dir=None,
):
    if log_dir is not None:
        return Path(
            log_dir
        )

    return (
        Path.home()
        / ".marvin"
        / "logs"
    )


def get_log_file(
    log_dir=None,
):
    return (
        get_log_dir(
            log_dir
        )
        / "marvin.log"
    )


def configure_logging(
    *,
    log_dir=None,
    level=None,
    console=None,
):
    logger = logging.getLogger(
        LOGGER_NAME
    )

    if getattr(
        logger,
        "_marvin_configured",
        False,
    ):
        configured_file = getattr(
            logger,
            "_marvin_log_file",
            None,
        )

        if configured_file:
            return Path(
                configured_file
            )

        return get_log_file(
            log_dir
        )


    resolved_level = (
        _resolve_level(
            level
        )
    )

    log_file = get_log_file(
        log_dir
    )


    try:
        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    except OSError:
        fallback = (
            Path(
                os.environ.get(
                    "TEMP",
                    ".",
                )
            )
            / "MARVIN"
            / "logs"
        )

        fallback.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_file = (
            fallback
            / "marvin.log"
        )


    formatter = logging.Formatter(
        (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(threadName)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=DEFAULT_MAX_BYTES,
        backupCount=DEFAULT_BACKUP_COUNT,
        encoding="utf-8",
    )

    file_handler.setLevel(
        resolved_level
    )

    file_handler.setFormatter(
        formatter
    )


    logger.setLevel(
        resolved_level
    )

    logger.propagate = False

    logger.addHandler(
        file_handler
    )


    if console is None:
        console = (
            sys.stderr is not None
            and hasattr(
                sys.stderr,
                "write",
            )
        )


    if console:
        console_handler = (
            logging.StreamHandler()
        )

        console_handler.setLevel(
            resolved_level
        )

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            console_handler
        )


    logger._marvin_configured = True
    logger._marvin_log_file = str(
        log_file
    )


    logger.info(
        "Logging inicializado em %s",
        log_file,
    )

    return log_file
