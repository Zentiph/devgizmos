# pylint: disable=too-many-lines

"""
decorators.__decorators
=======================

Module containing decorators.
"""

from functools import lru_cache, wraps
from logging import ERROR, INFO, WARNING, Logger
from platform import system
from re import findall
from statistics import mean
from time import perf_counter, perf_counter_ns, sleep
from typing import Any, Callable, TypeVar, get_type_hints
from warnings import warn

from ..checks import (
    check_callable,
    check_in_bounds,
    check_subclass,
    check_type,
    check_value,
)

if system() in ("Darwin", "Linux"):
    # pylint: disable=no-name-in-module
    from signal import SIGALRM, alarm, signal  # type: ignore
elif system() == "Windows":
    # pylint: disable=no-name-in-module
    from threading import Thread  # type: ignore


F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
LoggingLevel = int

TIME_UNITS = ("ns", "us", "ms", "s")
LOGGING_LEVELS = (
    0,  # NOTSET
    10,  # DEBUG
    20,  # INFO
    30,  # WARNING, WARN
    40,  # ERROR
    50,  # CRITICAL, FATAL
)

# TODO: ALLOW fmt TO BE NONE FOR NO MESSAGE


class ConditionError(Exception):
    """
    ConditionError
    ==============
    Error to raise when a necessary condition is not met.
    """


class UnsupportedOSError(Exception):
    """
    UnsupportedOSError
    ==================
    Error to raise when an unsupported OS is being used.
    Primary purpose is as a "catch all cases" solution, as it is unlikely this will ever be needed.
    """


# helper funcs
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


def _handle_result_reporting(fmt, default, logger, level, **kwargs):
    """
    _handle_result_reporting
    ========================
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


def timer(unit="ns", precision=3, *, fmt="", logger=None, level=INFO):
    """
    timer
    =====
    Times how long function it is decorated to takes to run.

    Parameter
    ---------
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
    >>> @timer()
    ... def perf_example():
    ...     sleep(0.001)
    ...
    >>> perf_example()
    [TIMER]: perf_example RAN IN 1277000.0 ns
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
            if local_unit not in TIME_UNITS:
                local_unit = "ns"

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
            default = f"[TIMER]: {func.__name__} RAN IN {rounded} {local_unit}"

            _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

            return result

        return wrapper

    return decorator


def benchmark(trials=10, unit="ns", precision=3, fmt="", logger=None, level=INFO):
    """
    benchmark
    =========
    Runs the function multiple times and reports average, min, and max execution times.

    Parameters
    ----------
    :param trials: The number of times to run the function, defaults to 10.
    :type trials: int
    :param unit: The unit of time to use, defaults to "ns".
    - Supported units are "ns", "us", "ms", "s".\n
    :type unit: Literal["ns", "us", "ms", "s"], optional
    :param precision: The precision to use when rounding the time, defaults to 3
    :type precision: int, optional
    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - trials: The number of trials ran.
    - avg: The average time of each trial.
    - min: The shortest time from the trials.
    - max: The longest time from the trials.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and raised {raised}."\n
    :type fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If trials is not an int.
    :raises TypeError: If precision is not an int.
    :raises TypeError: If fmt is not a str.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If trials is less than 1.
    :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> from time import sleep
    >>>
    >>> @benchmark()
    ... def perf_example():
    ...     sleep(0.001)
    ...
    >>> perf_example()
    [BENCHMARK]: RAN 10 TRIALS ON perf_example; AVG: 1089670.0 ns, MIN: 1025200.0 ns, MAX: 1140400.0 ns
    ```
    """

    # type checks
    check_type(trials, int)
    check_type(precision, int)
    check_type(fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_in_bounds(trials, 1, None)
    check_value(unit, TIME_UNITS)
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_unit = unit.lower()
            if local_unit not in TIME_UNITS:
                local_unit = "ns"

            results = []
            returned = [None]

            for i in range(trials):
                start_time = perf_counter_ns()

                if i == len(range(trials)) - 1:
                    returned[0] = func(*args, **kwargs)
                else:
                    func(*args, **kwargs)

                delta = perf_counter_ns() - start_time
                elapsed = delta / (1000 ** TIME_UNITS.index(local_unit))

                results.append(elapsed)

            avg_time = round(mean(results), precision)
            min_time = round(min(results), precision)
            max_time = round(max(results), precision)

            fmt_kwargs = {
                "name": func.__name__,
                "trials": trials,
                "avg": avg_time,
                "min": min_time,
                "max": max_time,
                "args": args,
                "kwargs": kwargs,
                "returned": repr(returned[0]),
            }
            default = (
                f"[BENCHMARK]: RAN {trials} TRIALS ON {func.__name__}; "
                f"AVG: {avg_time} {local_unit}, MIN: {min_time} {local_unit}, MAX: {max_time} {local_unit}"
            )

            _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

            return returned[0]

        return wrapper

    return decorator


def retry(
    max_attempts,
    delay,
    backoff_factor=1,
    *,
    exceptions=(Exception,),
    raise_last=True,
    success_fmt="",
    failure_fmt="",
    logger=None,
    level=INFO,
):
    """
    retry
    =====
    Retries a function if it fails up until the number of attempts is reached.

    Parameters
    ----------
    :param max_attempts: The maximum number of times to attempt running the decorated function,
    including the first time.
    :type max_attempts: int, optional
    :param delay: The time in seconds to wait after each retry.
    :type delay: int, optional
    :param backoff_factor: The amount to multiply the delay by after each attempt.
    :type backoff_factor: int | float
    :param exceptions: A tuple of the exceptions to catch and retry on, defaults to (Exception,)
    :type exceptions: Tuple[Type[BaseException], ...], optional
    :param raise_last: Whether to raise the final exception raised when all attempts fail,
    defaults to True
    :type raise_last: bool, optional
    :param success_fmt: Used to enter a custom success message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The number of attempts that ran.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: success_fmt="Func {name} took {attempts}/{max_attempts} attempts to run."\n
    :type success_fmt: str, optional
    :param failure_fmt: Used to enter a custom failure message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The current number of attempts.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - raised: The exception raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: failure_fmt="Func {name} failed at attempt {attempts}/{max_attempts}."\n
    :type failure_fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raise TypeError: If max_attempts is not an int.
    :raise TypeError: If delay is not an int or float.
    :raise TypeError: If backoff_factor is not an int or float.
    :raise TypeError: If exceptions is not a tuple.
    :raise TypeError: If an item inside exceptions is not a subclass of BaseException.
    :raise TypeError: If raise_last is not a bool.
    :raise TypeError: If success_fmt is not a str.
    :raise TypeError: If failure_fmt is not a str.
    :raise TypeError: If logger is not a logging.Logger.
    :raise ValueError: If max_attempts is less than 1.
    :raise ValueError: If delay is less than 0.
    :raise ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> @retry(3, 1)
    ... def risky():
    ...     raise TypeError
    ...
    >>> risky()
    [RETRY]: risky FAILED AT ATTEMPT 1/3; RAISED TypeError()
    [RETRY]: risky FAILED AT ATTEMPT 2/3; RAISED TypeError()
    [RETRY]: risky FAILED AT ATTEMPT 3/3; RAISED TypeError()
    TypeError
    ```
    """

    # type checks
    check_type(max_attempts, int)
    check_type(delay, int, float)
    check_type(backoff_factor, int, float)
    check_type(exceptions, tuple)
    check_subclass(BaseException, *exceptions)
    check_type(raise_last, bool)
    check_type(success_fmt, str)
    check_type(failure_fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_in_bounds(max_attempts, 1, None)
    check_in_bounds(delay, 0, None)
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            delay_ = delay

            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)

                    fmt_kwargs = {
                        "name": func.__name__,
                        "attempts": attempts + 1,
                        "max_attempts": max_attempts,
                        "exceptions": exceptions,
                        "args": args,
                        "kwargs": kwargs,
                        "returned": repr(result),
                    }
                    default = f"[RETRY]: {func.__name__} SUCCESSFULLY RAN AFTER {attempts + 1}/{max_attempts} ATTEMPTS"

                    _handle_result_reporting(
                        success_fmt, default, logger, level, **fmt_kwargs
                    )

                    return result

                except exceptions as e:
                    attempts += 1

                    fmt_kwargs = {
                        "name": func.__name__,
                        "attempts": attempts,
                        "max_attempts": max_attempts,
                        "exceptions": exceptions,
                        "raised": repr(e),
                        "args": args,
                        "kwargs": kwargs,
                    }
                    default = f"[RETRY]: {func.__name__} FAILED AT ATTEMPT {attempts}/{max_attempts}; RAISED {repr(e)}"

                    _handle_result_reporting(
                        failure_fmt, default, logger, level, **fmt_kwargs
                    )

                    if attempts >= max_attempts and raise_last:
                        raise

                    sleep(delay_)
                    delay_ *= backoff_factor

            return None

        return wrapper

    return decorator


def timeout(
    cutoff,
    *,
    success_fmt="",
    failure_fmt="",
    logger=None,
    success_level=INFO,
    failure_level=WARNING,
):
    """
    timeout
    =======
    Times out a function if it takes longer than the cutoff time to complete.
    Utilizes signal on Unix systems and threading on Windows.\n
    WARNING:
    On Windows, threading is much less reliable than signal and processes may
    still run to completion despite exceeding the cutoff time.

    Parameters
    ----------
    :param cutoff: The cutoff time, in seconds.
    :type cutoff: int | float
    :param success_fmt: Used to enter a custom success message format if changed, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.\n
    :type success_fmt: str, optional
    :param failure_fmt: Used to enter a custom failure message format if changed, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.\n
    :type failure_fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If cutoff is not an int or float.
    :raises TypeError: If success_fmt is not a str.
    :raises TypeError: If failure_fmt is not a str.
    :raises TypeError: If logger is not a Logger.
    :raises ValueError: If cutoff is 0 or less.
    :raises ValueError: If success_level is not a level from logging.
    :raises ValueError: If failure_level is not a level from logging.
    :raises TimeoutError: If the function's run time exceeds cutoff.
    :raises UnsupportedOSError: If system fails to determine the OS being used.

    Example Usage
    -------------
    ```python
    >>> from time import sleep
    >>>
    >>> @timeout(2)
    ... def long_process():
    ...     sleep(4)
    ...
    >>> long_process()
    [TIMEOUT]: long_process TIMED OUT AFTER 2 SECONDS
    TimeoutError: [TIMEOUT]: long_process TIMED OUT AFTER 2 SECONDS
    ```
    """

    # type checks
    check_type(cutoff, int, float)
    check_type(success_fmt, str)
    check_type(failure_fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_in_bounds(cutoff, 0, None, inclusive=False)
    check_value(success_level, LOGGING_LEVELS)
    check_value(failure_level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # unix implementation using signal
            if system() in ("Darwin", "Linux"):

                def _handle_timeout():
                    raise TimeoutError(
                        f"Function {func.__name__} timed out after {cutoff} seconds."
                    )

                original_handler = signal(SIGALRM, _handle_timeout)
                alarm(cutoff)

                try:
                    result = func(*args, **kwargs)
                    alarm(0)

                    fmt_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                        "args": args,
                        "kwargs": kwargs,
                    }
                    default = f"[TIMEOUT]: {func.__name__} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS"

                    _handle_result_reporting(
                        success_fmt, default, logger, success_level, **fmt_kwargs
                    )

                    return result

                except TimeoutError:
                    alarm(0)

                    fmt_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                        "args": args,
                        "kwargs": kwargs,
                    }
                    default = (
                        f"[TIMEOUT]: {func.__name__} TIMED OUT AFTER {cutoff} SECONDS"
                    )

                    _handle_result_reporting(
                        failure_fmt, default, logger, failure_level, **fmt_kwargs
                    )

                    raise

                finally:
                    signal(SIGALRM, original_handler)

            # windows implementation using threading (worse)
            if system() == "Windows":
                # initialize as lists to allow for modifications in nests
                result = [None]
                exc_raised = [False]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        result[0] = e
                        exc_raised[0] = True

                thread = Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(cutoff)
                if thread.is_alive():
                    thread.join()

                    fmt_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                        "args": args,
                        "kwargs": kwargs,
                    }
                    default = (
                        f"[TIMEOUT]: {func.__name__} TIMED OUT AFTER {cutoff} SECONDS"
                    )

                    _handle_result_reporting(
                        failure_fmt, default, logger, failure_level, **fmt_kwargs
                    )

                    raise TimeoutError(default)

                # handle unexpected exceptions
                if exc_raised[0]:
                    # pylint: disable=raising-bad-type
                    raise result[0]

                fmt_kwargs = {
                    "name": func.__name__,
                    "cutoff": cutoff,
                }
                default = f"[TIMEOUT]: {func.__name__} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS"

                _handle_result_reporting(
                    success_fmt, default, logger, success_level, **fmt_kwargs
                )

                return result[0]

            # if somehow not unix or windows, question everything
            raise UnsupportedOSError(
                "The detected OS is not Unix or Windows."
                + "If this is an unexpected issue, open an issue or send an email."
            )

        return wrapper

    return decorator


def cache(maxsize=None):
    """
    cache
    =====
    Caches the output of the decorated function and instantly returns it
    when given the same args and kwargs later.
    Uses LRU caching if a maxsize is provided.

    Parameters
    ----------
    :param maxsize: The maximum number of results to store in the cache using an LRU system, defaults to None.
    - Enter None for no size limitation.\n
    :type maxsize: int | None, optional

    Raises
    ------
    :raises TypeError: If maxsize is not an int or None.
    :raises ValueError: If maxsize is less than 1.

    Example Usage
    -------------
    ```python
    >>> from random import random
    >>>
    >>> @cache()
    ... def random_results(*args):
    ...     return random()
    ...
    >>> random_results()
    0.6741799332584445
    >>> random_results()
    0.6741799332584445
    >>> random_results(2)
    0.8902874918377771
    >>> random_results(2)
    0.8902874918377771
    ```
    """

    check_type(maxsize, int, optional=True)

    def decorator(func):
        cache_ = {}

        # if a maxsize is specified, use LRU caching
        if maxsize is not None:
            check_in_bounds(maxsize, 1, None)

            cached = lru_cache(maxsize)(func)
            return wraps(func)(cached)

        # otherwise use regular caching
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache_:
                return cache_[key]

            result = func(*args, **kwargs)
            cache_[key] = result
            return result

        return wrapper

    return decorator


def singleton():
    """
    singleton
    =========
    Ensures only one instance of a class can exist at once.

    Example Usage
    -------------
    ```python
    >>> @singleton()
    ... class Single:
    ...     def __init__(self, x):
    ...             self.x = x
    ...
    >>> s1 = Single(1)
    >>> s2 = Single(2)
    >>> s1.x
    1
    >>> s2.x
    1
    >>> s1 is s2
    True
    ```
    """

    instances = {}

    def decorator(cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]

        return wrapper

    return decorator


def type_checker():
    """
    type_checker
    ============
    Ensures the arguments passed to the decorated function are of the correct type based on the type hints.

    Raises
    ------
    :raises TypeError: If the args or kwargs passed do not match the function's type hints.
    :raises TypeError: If the return value does not match the function's type hints.

    Example Usage
    -------------
    >>> @type_checker()
    ... def typed_fun(a: int, b: float) -> str:
    ...     return str(a + b)
    ...
    >>> typed_fun(2, 1.0)
    '3.0'
    >>> typed_fun(3.2, 5)
    TypeError: Argument 'a' must be type 'int'
    """

    def decorator(func):
        hints = get_type_hints(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for name, value in zip(func.__code__.co_varnames, args):
                if name in hints and not isinstance(value, hints[name]):
                    raise TypeError(
                        f"Argument '{name}' must be type '{hints[name].__name__}'"
                    )

            for name, value in kwargs.items():
                if name in hints and not isinstance(value, hints[name]):
                    raise TypeError(
                        f"Argument '{name}' must be type '{hints[name].__name__}'"
                    )

            result = func(*args, **kwargs)

            if "return" in hints and not isinstance(result, hints["return"]):
                raise TypeError(
                    f"Return value must be type '{hints['return'].__name__}'"
                )
            return result

        return wrapper

    return decorator


def deprecated(reason, version=None, date=None):
    """
    deprecated
    ==========
    Creates a DeprecationWarning to show the decorated function or class is deprecated.

    Parameters
    ----------
    :param reason: The reason for deprecation.
    :type reason: str
    :param version: The version number of the function, defaults to None.
    :type version: int | float | str | None, optional
    :param date: The date of removal.
    :type date: str | None, optional

    Raises
    ------
    :raises TypeError: If reason is not a str.
    :raises TypeError: If version is not an int, float, str, or None.
    :raises TypeError: If date is not a str or None.

    Example Usage
    -------------
    >>> @deprecated("We found a better way to do this", "v1.0.3")
    ... def old_func(*args, **kwargs):
    ...     return all(args)
    ...
    >>> old_func(1, 2)
    <stdin>:1: DeprecationWarning: old_func is deprecated: We found a better way to do this (Ver: v1.0.3)
    True
    """

    # type checks
    check_type(reason, str)
    check_type(version, (int, float, str), optional=True)
    check_type(date, str, optional=True)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated: {reason}"
            if version:
                msg += f" (Ver: {version})"
            if date:
                msg += f" (Removal: {date})"

            warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def tracer(entry_fmt="", exit_fmt="", logger=None, level=INFO):
    """
    tracer
    ======
    Logs entries and exits of the decorated function.

    Parameters
    ----------
    :param entry_fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: entry_fmt="Entering func {name} with args={args} and kwargs={kwargs}."\n
    :type entry_fmt: str
    :param exit_fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: fmt="Exiting func {name} with args={args} and kwargs={kwargs}; Returned {returned}."\n
    :type exit_fmt: str
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.ERROR (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If entry_fmt is not a str.
    :raises TypeError: If exit_fmt is not a str.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> @tracer()
    ... def func(*args, **kwargs):
    ...     return all(args)
    ...
    >>> func(1, 2, word="Hello")
    [TRACER]: ENTERING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}
    [TRACER]: EXITING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}; RETURNED True
    True
    ```
    """

    # type checks
    check_type(entry_fmt, str)
    check_type(exit_fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            entry_fmt_kwargs = {
                "name": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            entry_default = (
                f"[TRACER]: ENTERING FUNC {func.__name__} WITH {args=} AND {kwargs=}"
            )
            _handle_result_reporting(
                entry_fmt, entry_default, logger, level, **entry_fmt_kwargs
            )

            result = func(*args, **kwargs)

            exit_fmt_kwargs = {
                "name": func.__name__,
                "args": args,
                "kwargs": kwargs,
                "returned": result,
            }
            exit_default = f"[TRACER]: EXITING FUNC {func.__name__} WITH {args=} AND {kwargs=}; RETURNED {result}"
            _handle_result_reporting(
                exit_fmt, exit_default, logger, level, **exit_fmt_kwargs
            )

            return result

        return wrapper

    return decorator


def error_logger(fmt="", suppress_=True, logger=None, level=ERROR):
    """
    error_logger
    ============
    Logs any errors that are raised by the decorated function.

    Parameters
    ----------
    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - raised: The error raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and raised {raised}."\n
    :type fmt: str, optional
    :param suppress: Whether to suppress the error raised or not, defaults to True.
    - If an error occurs and suppress if False, the decorated function will return None.\n
    :type suppress: bool, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.ERROR (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If fmt is not a str.
    :raises TypeError: If suppress is not a bool.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    >>> @error_logger()
    ... def risky():
    ...     raise TypeError
    ...
    >>> risky()
    [ERROR]: risky RAISED TypeError() WITH args=() AND kwargs={}
    """

    # type checks
    check_type(fmt, str)
    check_type(suppress_, bool)
    check_type(logger, Logger, optional=True)

    # value checks
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                fmt_kwargs = {
                    "name": func.__name__,
                    "raised": repr(e),
                    "args": args,
                    "kwargs": kwargs,
                }
                default = f"[ERROR]: {func.__name__} RAISED {repr(e)} WITH {args=} AND {kwargs=}"

                _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

                if not suppress_:
                    raise

                return None

        return wrapper

    return decorator


def decorate_all_methods(decorator, *args, **kwargs):
    """
    decorate_all_methods
    ====================
    Decorates all the methods in a class with the given decorator,
    ignoring magic/dunder methods.

    Parameters
    ----------
    :param decorator: The decorator to apply to each method.
    :type decorator: Decorator
    :param args: The arguments passed to the decorator.
    :type args: Any
    :param kwargs: The keyword arguments passed to the decorator.
    :type kwargs: Any

    Raises
    ------
    :raises TypeError: If decorator is not callable.

    Example Usage
    -------------
    >>> @decorate_all_methods(tracer, exit_fmt=None)
    ... class MyClass:
    ...     def __init__(self, a):
    ...             self.a = a
    ...     def __repr__(self):
    ...             return f"MyClass(a={self.a})"
    ...     def add_to_a(self, x):
    ...             self.a += x
    ...
    >>> cls = MyClass(1)
    >>> cls.add_to_a(2)
    [TRACER]: ENTERING add_to_a WITH args=(MyClass(a=3), 2) AND kwargs={}
    """

    # type checks
    check_callable(decorator)

    def decorator_(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not (
                attr_name.startswith("__") and attr_name.endswith("__")
            ):
                attr_value = decorator(*args, **kwargs)(attr_value)
                setattr(cls, attr_name, attr_value)

        return cls

    return decorator_


def rate_limit(*args):
    """
    rate_limit
    ==========
    Limits the number of times a function can be called in the given period.

    Parameters
    ----------
    :param interval: The time interval between each call (single argument).
    :type interval: int | float
    :param calls: The number of allowed calls in the period (first of two arguments).
    :type calls: int
    :param period: The time period in seconds (second of two arguments).
    :type period: int | float

    Raises
    ------
    :raises TypeError: If any number of args other than 1 or 2 are passed.
    :raises TypeError: If interval is not an int or float.
    :raises TypeError: If calls is not an int.
    :raises TypeError: If period if not an int or float.
    :raises ValueError: If interval is 0 or less.
    :raises ValueError: If calls is 0 or less.
    :raises ValueError: If period is 0 or less.

    Example Usage
    -------------
    ```python
    >>> from time import perf_counter
    >>>
    >>> @rate_limit(1)
    ... def get_time():
    ...     return perf_counter()
    ...
    >>> t1 = get_time()
    >>> t2 = get_time()
    >>> t2 - t1
    # the function will not be "re-callable"
    # for ~1 second each time it is called
    1.0003656
    ```
    """

    last_called = [0.0]

    # determine interval based off args length
    # or raise an exception if too many/little args
    if len(args) == 1:
        # type checks
        check_type(args[0], int, float)

        # value checks
        check_in_bounds(args[0], 0, None, inclusive=False)

        interval = args[0]
    elif len(args) == 2:
        # type checks
        check_type(args[0], int)
        check_type(args[1], int, float)

        # value checks
        check_in_bounds(args[0], 1, None)
        check_in_bounds(args[1], 0, None, inclusive=False)

        interval = float(args[0]) / float(args[1])
    else:
        raise TypeError(
            f"rate_limit() takes 1 or 2 positional arguments but {len(args)} were given"
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = perf_counter() - last_called[0]
            wait = interval - elapsed

            if wait > 0:
                sleep(wait)

            last_called[0] = perf_counter()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def suppress(*exceptions, fmt="", logger=None, level=INFO):
    """
    suppress
    ========
    Suppresses any of the given exceptions, returning None if they occur.

    Parameters
    ----------
    :param exceptions: The exceptions to suppress if they occurs.
    :type exceptions: Type[Exception]
    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - raised: The error raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and raised {raised}."\n
    :type fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.ERROR (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If any of the exceptions are not a subclass of BaseException.
    :raises TypeError: If fmt is not a str.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> @suppress(ZeroDivisionError)
    ... def divide(x, y):
    ...     return x / y
    ...
    >>> divide(1, 0)  # will not raise an exception
    [SUPPRESS]: SUPPRESSED ZeroDivisionError('division by zero') RAISED BY FUNC divide WITH args=(1, 0) AND kwargs={}
    ```
    """

    # type checks
    check_subclass(BaseException, *exceptions)
    check_type(fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_value(level, LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                fmt_kwargs = {
                    "name": func.__name__,
                    "raised": repr(e),
                    "args": args,
                    "kwargs": kwargs,
                }
                default = f"[SUPPRESS]: SUPPRESSED {repr(e)} RAISED BY FUNC {func.__name__} WITH {args=} AND {kwargs=}"

                _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

                return None

        return wrapper

    return decorator


def conditional(condition, *, raise_exc=False):
    """
    conditional
    ===========
    Executes the decorated function only if the condition is met.

    Parameters
    ----------
    :param condition: The condition to meet.
    :type condition: Callable[..., bool]
    :param raise_exc: Whether to raise an exception if the condition is not met, defaults to False.
    :type raise_exc: bool, optional

    Raises
    ------
    :raises TypeError: If condition is not callable.
    :raises TypeError: If raise_exc is not a bool.
    :raises ConditionError: If the condition is not met and raise_exc is True.

    Example Usage
    -------------
    ```python
    >>> @conditional(lambda x: x > 0, raise_exc=True)
    ... def positives_only(x):
    ...     return x
    ...
    >>> positives_only(1)
    1
    >>> positives_only(-1)
    ConditionError: Condition was not met: <lambda> args=(-1,) kwargs={}
    ```
    """

    # type checks
    if not callable(condition):
        raise TypeError("'condition' must be callable")
    check_type(raise_exc, bool)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return func(*args, **kwargs)

            if raise_exc:
                raise ConditionError(
                    f"Condition was not met: {condition.__name__} {args=} {kwargs=}"
                )

            return None

        return wrapper

    return decorator
