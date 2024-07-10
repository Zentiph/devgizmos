"""
_internal.__internals
=====================
Contains re-used internal functionality.
"""

from logging import INFO
from re import findall

TIME_UNITS = ("ns", "us", "ms", "s")
LOGGING_LEVELS = (
    0,  # NOTSET
    10,  # DEBUG
    20,  # INFO
    30,  # WARNING, WARN
    40,  # ERROR
    50,  # CRITICAL, FATAL
)


def _print_msg(fmt, default, **kwargs):
    """
    _print_msg
    ==========
    Helper function used to print messages.

    Parameters
    ----------
    :param fmt: The format for the message.
    :type fmt: str
    :param default: The default message.
    :type default: str
    :param kwargs: The kwargs to be formatted into the message.
    :type kwargs: Any
    """

    msg = None
    if fmt:
        msg = fmt.format(**kwargs)
    elif fmt == "":
        msg = default

    if msg:
        print(msg)


def _handle_logging(fmt, default, logger=None, level=INFO, **values):
    """
    _handle_logging
    ===============
    Helper function used to handle logging operations.

    Parameters
    ----------
    :param fmt: The message format.
    :type fmt: str
    :param default: The default message format.
    :type default: str
    :param logger: The logger to use.
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional
    :param values: The names and values to place in the message using '%s' formatting.
    :type values: Any
    """

    if fmt == "":
        fmt = default

    # finds all values inside brackets but
    # doesn't go deeper than 1 layer
    # to prevent it from finding dicts
    str_vars = findall(r"\{(\w+)\}", fmt)
    logging_formatter = fmt

    for str_var in str_vars:
        logging_formatter = logging_formatter.replace(f"{{{str_var}}}", "%s")

    args = tuple(values[str_var] for str_var in str_vars)

    logger.log(level, logging_formatter, *args)


def handle_result_reporting(fmt, default, logger, level, **kwargs):
    """
    handle_result_reporting
    =======================
    Handles result reporting for decorators.

    Parameters
    ----------
    :param fmt: The message format.
    :type fmt: str
    :param default: The default message.
    :type default: str
    :param logger: The logger to use.
    :type logger: Logger | None
    :param level: The logging level.
    :type level: LoggingLevel
    """

    if logger is not None:
        _handle_logging(fmt, default, logger, level, **kwargs)
    else:
        _print_msg(fmt, default, **kwargs)
