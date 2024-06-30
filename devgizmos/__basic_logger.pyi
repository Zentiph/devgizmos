# pylint: disable=all

import logging
from typing import Union

LoggingLevel = int

class BasicLogger(logging.Logger):
    def __init__(
        self,
        level: LoggingLevel = logging.DEBUG,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None: ...
