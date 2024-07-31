"""
basic_logger
============
Module containing an already set up logger to skip the few set up lines of code needed when testing basic logging.
"""

from logging import DEBUG, Formatter, Logger, StreamHandler

from .errguards import ensure_instance_of, ensure_value

LoggingLevel = int
LOGGING_LEVELS = (0, 10, 20, 30, 40, 50)


class BasicLogger(Logger):
    """
    Logger for quickly testing/logging.
    """

    def __init__(
        self, level=DEBUG, fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        """
        BasicLogger()
        -------------
        Logger for quickly testing/logging.
        Child class of logging.Logger.

        Parameters
        ~~~~~~~~~~
        :param level: The logging level, defaults to logging.DEBUG
        :type level: LoggingLevel, optional
        :param fmt: The logging format, defaults to "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        :type fmt: str, optional
        """

        # type checks
        ensure_instance_of(level, LoggingLevel)
        ensure_instance_of(fmt, str)

        # value checks
        ensure_value(level, LOGGING_LEVELS)

        super().__init__("BasicLogger", level)

        self._handler = StreamHandler()
        self._handler.setLevel(DEBUG)
        self._handler.setFormatter(Formatter(fmt))
        self.addHandler(self._handler)
