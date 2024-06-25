"""
basic_logger
============

Module containing an already set up logger to skip the few set up lines of code needed when testing basic logging.

This module utilizes the following functionality from built-in modules/packages:

logging
- DEBUG
- Formatter
- Logger
- StreamHandler

typing
- Union
"""

from logging import DEBUG, Formatter, Logger, StreamHandler
from typing import Union

from .checks import check_types, check_values

LoggingLevel = Union[int, str]
LOGGING_LEVELS = (0, 10, 20, 30, 40, 50)


class BasicLogger(Logger):
    """The logger to use when quickly testing logging."""

    def __init__(
        self, level=DEBUG, fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        """
        Initializer for a BasicLogger object.

        :param level: The logging level, defaults to logging.DEBUG

        :type level: LoggingLevel, optional

        :param fmt: The logging format, defaults to "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        :type fmt: str, optional
        """

        # type checks
        check_types(level, LoggingLevel)
        check_types(fmt, str)

        # value checks
        check_values(level, *LOGGING_LEVELS)

        super().__init__("BasicLogger", level)

        self._handler = StreamHandler()
        self._handler.setLevel(DEBUG)
        self._handler.setFormatter(Formatter(fmt))
        self.addHandler(self._handler)
