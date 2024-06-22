# pylint: disable=all

from logging import DEBUG, Logger
from typing import Union

LoggingLevel = Union[int, str]

class BasicLogger(Logger):
    def __init__(
        self,
        level: LoggingLevel = DEBUG,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None: ...
