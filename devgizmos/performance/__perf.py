"""
performance.__perf
==================
Module containing performance related functionality.
"""

from functools import wraps
from inspect import currentframe
from logging import INFO, Logger
from time import perf_counter_ns

from .._internal import LOGGING_LEVELS, TIME_UNITS, handle_result_reporting
from ..checks import check_type, check_value


# pylint: disable=too-many-instance-attributes
class Timer:
    """Context manager for timing code."""

    def __init__(self, unit="ns", precision=3, *, fmt="", logger=None, level=INFO):
        """
        Timer
        =====
        Context manager that times how long the code inside takes to run.
        For a decorator version, see dectimer.

        Parameters
        ----------
        :param unit: The unit of time to use, defaults to "ns".
        - Supported units are "ns", "us", "ms", "s".\n
        :type unit: Literal["ns", "us", "ms", "s"], optional
        :param precision: The precision to use when rounding the time, defaults to 3
        :type precision: int, optional
        :param fmt: Used to enter a custom message format, defaults to "".
        - Leave as an empty string to use the pre-made message.
        - Enter an unformatted string with the following fields to include their values
        - line: The line the Timer was called on.
        - elapsed: The time elapsed by the code's execution.
        - unit: The unit used in the timing.
        - Ex: fmt="Code from lines {enter}-{exit} took {elapsed} {unit} to run."\n
        :type fmt: str, optional
        :param logger: The logger to use if desired, defaults to None.
        - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
        :type logger: Logger | None, optional
        :param level: The logging level to use, defaults to logging.INFO (20).
        :type level: LoggingLevel, optional

        Raises
        ------
        :raises TypeError: If precision is not an int.
        :raises TypeError: If fmt is not a str.
        :raises TypeError: If logger is not a logging.Logger.
        :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.
        :raises ValueError: If level is not a level from logging.

        Example Usage
        -------------
        ```python
        >>> with Timer("ms") as t:
        ...     for _ in range(100_000):
        ...             pass
        ...     # pause the timer
        ...     t.pause()
        ...     # get the current elapsed time
        ...     print(t.elapsed)
        ...     for _ in range(100_000):
        ...             pass
        ...     # resume the timer
        ...     t.resume()
        ...     for _ in range(100_000):
        ...             pass
        ...
        3.196
        [TIMER]: CODE STARTING AT LINE 1 RAN IN 6.214 ms
        ```
        """

        # type checks
        check_type(precision, int)
        check_type(fmt, str)
        check_type(logger, Logger, optional=True)

        unit = unit.lower()
        # value checks
        check_value(unit, TIME_UNITS)
        check_value(level, LOGGING_LEVELS)

        self.__unit = unit
        self.__precision = precision
        self.__fmt = fmt
        self.__logger = logger
        self.__level = level

        self.__initial_time = 0.0  # placeholder, see __enter__
        self.__last_unpaused = 0.0  # placeholder, see __enter__
        self.__elapsed_time = 0.0
        self.__paused = False

        self.__line = currentframe().f_back.f_lineno

    def __enter__(self):
        self.__initial_time = perf_counter_ns()
        self.__last_unpaused = self.__initial_time

        return self

    def __exit__(self, type_, value, traceback):
        self.pause()
        converted = self.__elapsed_time / (1000 ** TIME_UNITS.index(self.__unit))
        rounded = round(converted, self.__precision)

        fmt_kwargs = {
            "line": self.__line,
            "elapsed": rounded,
            "unit": self.__unit,
        }
        default = f"[TIMER]: CODE STARTING AT LINE {self.__line} RAN IN {rounded} {self.__unit}"

        handle_result_reporting(
            self.__fmt, default, self.__logger, self.__level, **fmt_kwargs
        )

    @property
    def elapsed(self):
        """
        Timer.elapsed()
        ===============
        Returns the time elapsed so far.
        """

        if not self.__paused:
            now = perf_counter_ns()
            self.__elapsed_time += now - self.__last_unpaused
            self.__last_unpaused = now

        converted = self.__elapsed_time / (1000 ** TIME_UNITS.index(self.__unit))
        rounded = round(converted, self.__precision)

        return rounded

    def pause(self):
        """
        Timer.pause()
        =============
        Pauses the timer.
        """

        if not self.__paused:
            self.__elapsed_time += perf_counter_ns() - self.__last_unpaused
            self.__paused = True

    def resume(self):
        """
        Timer.resume()
        ==============
        Resumes the timer.
        """

        self.__last_unpaused = perf_counter_ns()
        self.__paused = False


def dectimer(unit="ns", precision=3, *, fmt="", logger=None, level=INFO):
    """
    dectimer
    ========
    Times how long function it is decorated to takes to run.
    For a context manager version, see Timer.

    Parameters
    ----------
    :param unit: The unit of time to use, defaults to "ns".
    - Supported units are "ns", "us", "ms", "s".\n
    :type unit: Literal["ns", "us", "ms", "s"], optional
    :param precision: The precision to use when rounding the time, defaults to 3
    :type precision: int, optional
    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - elapsed: The time elapsed by the function's execution.
    - unit: The unit used in the timing.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: fmt="Func {name} took {elapsed} {unit} to run and returned {returned}."\n
    :type fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If precision is not an int.
    :raises TypeError: If fmt is not a str.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> from time import sleep
    >>>
    >>> @dectimer()
    ... def perf_example():
    ...     sleep(0.001)
    ...
    >>> perf_example()
    [DECTIMER]: perf_example RAN IN 1277000.0 ns
    ```
    """

    # type checks
    check_type(precision, int)
    check_type(fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_value(unit, TIME_UNITS)
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_unit = unit.lower()

            start_time = perf_counter_ns()
            result = func(*args, **kwargs)

            delta = perf_counter_ns() - start_time
            elapsed = delta / (1000 ** TIME_UNITS.index(local_unit))
            rounded = round(elapsed, precision)

            fmt_kwargs = {
                "name": func.__name__,
                "elapsed": rounded,
                "unit": local_unit,
                "args": args,
                "kwargs": kwargs,
                "returned": repr(result),
            }
            default = f"[DECTIMER]: {func.__name__} RAN IN {rounded} {local_unit}"

            handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

            return result

        return wrapper

    return decorator
