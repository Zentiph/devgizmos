"""
basic_logger
============
Module containing an already set up logger to skip the few set up lines of code needed when testing basic logging.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:
logging
- DEBUG
- Formatter
- Logger
- StreamHandler\n
typing
- Union
"""

from logging import DEBUG, Formatter, Logger, StreamHandler
from typing import Union

from .checks import check_type, check_value

LoggingLevel = Union[int, str]
LOGGING_LEVELS = (0, 10, 20, 30, 40, 50)


class BasicLogger(Logger):
    """
    BasicLogger
    ===========
    Logger for quickly testing/logging.
    """

    def __init__(
        self, level=DEBUG, fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        """
        BasicLogger
        ===========
        Logger for quickly testing/logging.

        Parameters
        ----------
        :param level: The logging level, defaults to logging.DEBUG
        :type level: LoggingLevel, optional
        :param fmt: The logging format, defaults to "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        :type fmt: str, optional
        """

        # type checks
        check_type(level, LoggingLevel)
        check_type(fmt, str)

        # value checks
        check_value(level, LOGGING_LEVELS)

        super().__init__("BasicLogger", level)

        self._handler = StreamHandler()
        self._handler.setLevel(DEBUG)
        self._handler.setFormatter(Formatter(fmt))
        self.addHandler(self._handler)
