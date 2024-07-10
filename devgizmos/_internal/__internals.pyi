# pylint: disable=all

from logging import INFO, Logger
from re import findall
from typing import Any, Literal, Optional, Tuple

LoggingLevel = int

TIME_UNITS: Tuple[Literal["ns"], Literal["us"], Literal["ms"], Literal["s"]]
LOGGING_LEVELS: Tuple[
    Literal[0], Literal[10], Literal[20], Literal[30], Literal[40], Literal[50]
]

def handle_result_reporting(
    fmt: str, default: str, logger: Optional[Logger], level: LoggingLevel, **kwargs: Any
): ...
