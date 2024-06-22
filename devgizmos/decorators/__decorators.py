"""decorators.__decorators
------------------------
Module containing decorators.
"""

from functools import lru_cache, wraps
from logging import ERROR, INFO, WARNING, Logger
from platform import system
from re import findall
from statistics import mean
from time import perf_counter, perf_counter_ns, sleep
from typing import Any, Callable, TypeVar, Union, get_type_hints
from warnings import warn

from ..checks import check_in_bounds, check_types, check_values

if system() in ("Darwin", "Linux"):
    # pylint: disable=no-name-in-module
    from signal import SIGALRM, alarm, signal  # type: ignore
elif system() == "Windows":
    # pylint: disable=no-name-in-module
    from threading import Thread  # type: ignore


__all__ = [
    "timer",
    "benchmark",
    "retry",
    "timeout",
    "cache",
    "singleton",
    "type_checker",
    "deprecated",
    "call_logger",
    "error_logger",
    "decorate_all_methods",
    "rate_limit",
]

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
LoggingLevel = Union[int, str]

TIME_UNITS = ("ns", "us", "ms", "s")
LOGGING_LEVELS = (
    0,  # NOTSET
    10,  # DEBUG
    20,  # INFO
    30,  # WARNING, WARN
    40,  # ERROR
    50,  # CRITICAL, FATAL
)


class UnsupportedOSError(Exception):
    """Error to raise when an unsupported OS is used for the timeout decorator."""


# helper funcs
def _print_msg(fmt, default, **kwargs):
    """Helper function used to print messages.

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
    """Helper function used to handle logging operations.

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
    """Handles result reporting for decorators.

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
    """decorators.timer
    -------------------
    Times how long function it is decorated to takes to run.

    :param unit: The unit of time to use, defaults to "ns".
    - Supported units are "ns", "us", "ms", "s".
    - If an invalid unit is provided, unit will default to "ns".

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
    - Ex: fmt="Func {name} took {elapsed} {unit} to run and returned {returned}."

    :type fmt: str, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.INFO (20).

    :type level: LoggingLevel, optional
    """

    # type checks
    check_types(unit, str)
    check_types(precision, int)
    check_types(fmt, str)
    check_types(logger, Logger, optional=True)
    check_types(level, LoggingLevel)

    # value checks
    check_values(unit, *TIME_UNITS)
    check_values(level, *LOGGING_LEVELS)

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
    """decorators.benchmark
    -----------------------
    Runs the function multiple times and reports average, min, and max execution times.

    :param trials: The number of times to run the function, defaults to 10.

    :type trials: int

    :param unit: The unit of time to use, defaults to "ns".
    - Supported units are "ns", "us", "ms", "s".
    - If an invalid unit is provided, unit will default to "ns".

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
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and raised {raised}."

    :type fmt: str, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.INFO (20).

    :type level: LoggingLevel, optional
    """

    # type checks
    check_types(trials, int)
    check_types(unit, str)
    check_types(precision, int)
    check_types(fmt, str)
    check_types(logger, Logger, optional=True)
    check_types(level, LoggingLevel)

    # value checks
    check_in_bounds(trials, 1, None)
    check_values(unit, *TIME_UNITS)
    check_values(level, *LOGGING_LEVELS)

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
                rounded = round(elapsed, precision)

                results.append(rounded)

            avg_time = mean(results)
            min_time = min(results)
            max_time = max(results)

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
                + f"AVG: {avg_time} {local_unit}, MIN: {min_time} {local_unit}, MAX: {max_time}, {local_unit}"
            )

            _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

            return returned[0]

        return wrapper

    return decorator


def retry(
    max_attempts=3,
    delay=1,
    *,
    exceptions=(Exception,),
    raise_last=True,
    success_fmt="",
    failure_fmt="",
    logger=None,
    level=INFO,
):
    """decorators.retry
    -------------------
    Retries a function if it fails up until the number of attempts is reached.

    :param max_attempts: The maximum number of times to attempt running the decorated function,
    including the first time, defaults to 3

    :type max_attempts: int, optional

    :param delay: The time in seconds to wait after each retry, defaults to 1

    :type delay: int, optional

    :param exceptions: A tuple of the exceptions to catch and retry on, defaults to (Exception,)

    :type exceptions: Tuple[Type[Exception], ...], optional

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
    - Ex: success_fmt="Func {name} took {attempts}/{max_attempts} attempts to run."

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
    - Ex: failure_fmt="Func {name} failed at attempt {attempts}/{max_attempts}."

    :type failure_fmt: str, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.INFO (20).

    :type level: LoggingLevel, optional
    """

    # type checks
    check_types(max_attempts, int)
    check_types(delay, int, float)
    check_types(exceptions, tuple)
    for exc in exceptions:
        check_types(exc, type)
    check_types(raise_last, bool)
    check_types(success_fmt, str)
    check_types(failure_fmt, str)
    check_types(logger, Logger, optional=True)
    check_types(level, LoggingLevel)

    # value checks
    check_in_bounds(max_attempts, 1, None)
    check_in_bounds(delay, 0, None)
    check_values(level, *LOGGING_LEVELS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0

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

                    sleep(delay)

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
    """decorators.timeout
    ---------------------
    Times out a function if it takes longer than the cutoff time to complete.
    Utilizes signal on Unix systems and threading on Windows.

    WARNING:
    On Windows, threading is much less reliable than signal and many processes will
    still complete despite exceeding the cutoff time. This is unfortunately not fixable.

    :param cutoff: The cutoff time, in seconds.

    :type cutoff: int | float

    :param success_fmt: Used to enter a custom success message format if changed, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.

    :type success_fmt: str, optional

    :param failure_fmt: Used to enter a custom failure message format if changed, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.

    :type failure_fmt: str, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.INFO (20).

    :type level: LoggingLevel, optional
    """

    # type checks
    check_types(cutoff, int, float)
    check_types(success_fmt, str)
    check_types(failure_fmt, str)
    check_types(logger, Logger)
    check_types(success_level, LoggingLevel)
    check_types(failure_level, LoggingLevel)

    # value checks
    check_in_bounds(cutoff, 0, None)
    check_values(success_level, *LOGGING_LEVELS)
    check_values(failure_level, *LOGGING_LEVELS)

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
    """decorators.cache
    -------------------

    Caches the output of the decorated function and instantly returns it
    when given the same args and kwargs later.
    Will use LRU caching if a maxsize is provided.

    :param maxsize: The maximum number of results to store in the cache using an LRU system, defaults to None.
    - Enter None for no size limitation.

    :type maxsize: int] | None optional
    """

    check_types(maxsize, int, optional=True)

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
    """decorators.singleton
    -----------------------

    Ensures only one instance of a class can exist at once.
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
    """decorators.type_checker
    --------------------------

    Ensures the arguments passed to the decorated function are of the correct type based on the type hints.
    """

    def decorator(func):
        hints = get_type_hints(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for name, value in zip(func.__code__.co_varnames, args):
                if name in hints and not isinstance(value, hints[name]):
                    raise TypeError(f"Argument {name} must be {hints[name].__name__}")

            for name, value in kwargs.items():
                if name in hints and not isinstance(value, hints[name]):
                    raise TypeError(f"Argument {name} must be {hints[name].__name__}")

            result = func(*args, **kwargs)

            if "return" in hints and not isinstance(result, hints["return"]):
                raise TypeError(f"Return value must be {hints['return'].__name__}")
            return result

        return wrapper

    return decorator


def deprecated(reason, version=None, date=None):
    """decorators.deprecated
    ------------------------

    Creates a DeprecationWarning to show the decorated function or class is deprecated.

    :param reason: The reason for deprecation.

    :type reason: str

    :param version: The version number of the function, defaults to None.

    :type version: int | float | str | None, optional

    :param date: The date of removal.

    :type date: str | None, optional
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated: {reason}"
            if version:
                msg += f"(Version: {version})"
            if date:
                msg += f"(Removal Date: {date})"

            warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def call_logger(fmt="", logger=None, level=INFO):
    """decorators.call_logger
    -------------------------

    Logs each time the decorated function is called.

    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and returned {returned}."

    :type fmt: str, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.INFO (20).

    :type level: LoggingLevel, optional
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            fmt_kwargs = {
                "name": func.__name__,
                "args": args,
                "kwargs": kwargs,
                "returned": result,
            }
            default = f"[CALL]: {func.__name__} CALLED WITH {args=} AND {kwargs=}; RETURNED {result}"

            _handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

            return result

        return wrapper

    return decorator


def error_logger(fmt="", suppress=True, logger=None, level=ERROR):
    """decorators.error_logger
    --------------------------

    Logs any errors that are raised by the decorated function.

    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - raised: The error raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: fmt="Func {name} was called with args={args} and kwargs={kwargs} and raised {raised}."

    :type fmt: str, optional

    :param suppress: Whether to suppress the error raised or not, defaults to True.
    - If an error occurs and suppress if False, the decorated function will return None.

    :type suppress: bool, optional

    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.

    :type logger: Logger | None optional

    :param level: The logging level to use, defaults to logging.ERROR (20).

    :type level: LoggingLevel, optional
    """

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

                if not suppress:
                    raise

                return None

        return wrapper

    return decorator


def decorate_all_methods(decorator, *dec_args, **dec_kwargs):
    """decorators.decorate_all_methods
    ----------------------------------

    Decorates all the methods in a class with the given decorators.
    The first decorator is the inner-most decorator,
    continuing until the final decorator which is the outer-most decorator.

    :param decorator: The decorator to apply to each method.

    :type decorator: Decorator

    :param dec_args: The arguments passed to the decorator.

    :type dec_args: Any

    :param dec_kwargs: The keyword arguments passed to the decorator.

    :type dec_kwargs: Any
    """

    def decorator_(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                attr_value = decorator(*dec_args, **dec_kwargs)(attr_value)
                setattr(cls, attr_name, attr_value)

        return cls

    return decorator_


def rate_limit(calls, period):
    """decorators.rate_limit
    ------------------------
    Limits the number of times a function can be called in the given period.

    :param calls: The number of allowed calls in the period.

    :type calls: int

    :param period: The time period in seconds.

    :type period: int | float
    """

    interval = float(period) / float(calls)
    last_called = [0.0]

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
