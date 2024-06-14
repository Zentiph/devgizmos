# pylint: disable=all

from logging import DEBUG, Logger

LoggingLevel = int | str

class BasicLogger(Logger):
    def __init__(
        self,
        level: LoggingLevel = DEBUG,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None: ...
