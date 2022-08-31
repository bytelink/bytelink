from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path

import coloredlogs  # type: ignore # pyright complains if this isn't installed

import bytelink.config

LOG_LEVEL = logging.DEBUG if bytelink.config.DEBUG else logging.INFO
LOG_FILE = bytelink.config.LOG_FILE
LOG_FILE_MAX_SIZE = bytelink.config.LOG_FILE_MAX_SIZE
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)7s | %(message)s"


def setup_logging() -> None:
    """Sets up logging library to use our log format and defines log levels."""
    root_log = logging.getLogger()
    log_formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
        coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT

    if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            "critical": {"background": "red"},
        }

    coloredlogs.install(level=logging.DEBUG, logger=root_log, stream=sys.stdout)

    if LOG_FILE is not None:
        file_handler = logging.handlers.RotatingFileHandler(Path(LOG_FILE), maxBytes=LOG_FILE_MAX_SIZE)
        file_handler.setFormatter(log_formatter)
        root_log.addHandler(file_handler)

    root_log.setLevel(LOG_LEVEL)
