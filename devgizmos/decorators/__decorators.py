"""decorators.decorators
------------------------
Module containing decorators.
"""

from functools import wraps
from logging import getLogger
from platform import system
from time import perf_counter_ns, sleep
from typing import get_type_hints
from warnings import warn

from ..checks import verify_types, verify_values

if system() in ("Darwin", "Linux"):
    # pylint: disable=no-name-in-module
    from signal import SIGALRM, alarm, signal  # type: ignore
elif system() == "Windows":
    # pylint: disable=no-name-in-module
    from threading import Thread  # type: ignore


__all__ = [
    "timer",
    "retry",
    "timeout",
    "cache",
    "singleton",
    "type_checker",
    "deprecated",
    "log_calls",
]

TIMER_UNITS = ("ns", "us", "ms", "s")


class _UnsupportedOSError(Exception):
    """Error to raise when an unsupported OS is used for the timeout decorator."""


# helper funcs
def _print_msg(format_, default, **kwargs):
    """Internal function used to print messages.

    :param format_: The format for the message.

    :type format_: str

    :param default: The default message.

    :type default: str

    :param kwargs: The kwargs to be formatted into the message.
    """

    msg = None
    if format_:
        msg = format_.format(**kwargs)
    elif format_ == "":
        msg = default

    if msg:
        print(msg)


def timer(unit="ns", precision=0, *, msg_format="", logger=None):
    """decorators.timer
    -------------------
    Times how long function it is decorated to takes to run.

    :param unit: The unit of time to use, defaults to "ns"
    - Supported units are "ns", "us", "ms", "s"
    - If an invalid unit is provided, unit will default to "ns".

    :type unit: str, optional

    :param precision: The precision to use when rounding the time, defaults to 0

    :type precision: int, optional

    :param msg_format: Used to enter a custom message format, defaults to ""
    - Enter None for an empty message; leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - elapsed: The time elapsed by the function's execution.
    - unit: The unit used in the timing.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: msg_format="Func {name} took {elapsed} {unit} to run and returned {returned}."

    :type msg_format: str, optional

    :param logger: The logger to use if desired, defaults to None.

    :type logger: Optional[Logger], optional
    """

    # type checks
    verify_types(unit, str)
    verify_types(precision, int)
    verify_types(msg_format, str)

    # value checks
    verify_values(unit, *TIMER_UNITS)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_unit = unit.lower()
            if local_unit not in TIMER_UNITS:
                local_unit = "ns"

            start_time = perf_counter_ns()
            result = func(*args, **kwargs)

            delta = perf_counter_ns() - start_time
            elapsed = delta / (1000 ** TIMER_UNITS.index(local_unit))
            rounded = round(elapsed, precision)

            msg_kwargs = {
                "name": func.__name__,
                "elapsed": rounded,
                "unit": local_unit,
                "args": args,
                "kwargs": kwargs,
                "returned": repr(result),
            }

            _print_msg(
                msg_format,
                f"[TIMER]: {func.__name__} RAN IN {rounded} {local_unit}",
                **msg_kwargs,
            )

            return result

        return wrapper

    return decorator


def retry(
    max_attempts=3,
    delay=1,
    *,
    exceptions=(Exception,),
    raise_last=True,
    success_msg_format="",
    failure_msg_format="",
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

    :param success_msg_format: Used to enter a custom success message format, defaults to ""
    - Enter None for an empty message; leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The number of attempts that ran.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: success_msg_format="Func {name} took {attempts}/{max_attempts} attempts to run."

    :type success_msg_format: str, optional

    :param failure_msg_format: Used to enter a custom failure message format, defaults to ""
    - Enter None for an empty message; leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The current number of attempts.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - raised: The exception raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: failure_msg_format="Func {name} failed at attempt {attempts}/{max_attempts}."

    :type failure_msg_format: str, optional

    """

    # type checks
    verify_types(max_attempts, int)
    verify_types(delay, int, float)
    verify_types(exceptions, tuple)
    for exc in exceptions:
        verify_types(exc, type)
    verify_types(raise_last, bool)
    verify_types(success_msg_format, str)
    verify_types(failure_msg_format, str)

    # value checks
    if max_attempts < 1:
        raise ValueError("max_attempts cannot be less than 1.")
    if delay < 0:
        raise ValueError("delay cannot be less than 0.")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0

            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)

                    msg_kwargs = {
                        "name": func.__name__,
                        "attempts": attempts + 1,
                        "max_attempts": max_attempts,
                        "exceptions": exceptions,
                        "args": args,
                        "kwargs": kwargs,
                        "returned": repr(result),
                    }

                    _print_msg(
                        success_msg_format,
                        f"[RETRY]: {func.__name__} SUCCESSFULLY RAN AFTER {attempts + 1}/{max_attempts} ATTEMPTS",
                        **msg_kwargs,
                    )

                    return result

                except exceptions as e:
                    attempts += 1

                    msg_kwargs = {
                        "name": func.__name__,
                        "attempts": attempts,
                        "max_attempts": max_attempts,
                        "exceptions": exceptions,
                        "raised": repr(e),
                        "args": args,
                        "kwargs": kwargs,
                    }

                    _print_msg(
                        failure_msg_format,
                        f"[RETRY]: {func.__name__} FAILED AT ATTEMPT {attempts}/{max_attempts}; RAISED {repr(e)}",
                        **msg_kwargs,
                    )

                    if attempts >= max_attempts and raise_last:
                        raise

                    sleep(delay)

            return None

        return wrapper

    return decorator


def timeout(cutoff, *, success_msg_format="", failure_msg_format=""):
    """decorators.timeout
    ---------------------
    Times out a function if it takes longer than the cutoff time to complete.
    Utilizes signal on Unix systems; utilizes threading on Windows.
    Raises a TimeoutError by default. Enter a different exception type
    to change the exception, or None to not raise an exception.

    :param cutoff: The cutoff time, in seconds.

    :type cutoff: Union[int, float]

    :param success_msg_format: Used to enter a custom success message format if changed, defaults to ""
    - Enter None for an empty message; leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.

    :type success_msg_format: str, optional

    :param failure_msg_format: Used to enter a custom failure message format if changed, defaults to ""
    - Enter None for an empty message; leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.

    :type failure_msg_format: str, optional
    """

    # type checks
    verify_types(cutoff, int, float)
    verify_types(success_msg_format, str)
    verify_types(failure_msg_format, str)

    # value checks
    if cutoff < 0:
        raise ValueError("cutoff cannot be less than 0.")

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

                    msg_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                    }

                    _print_msg(
                        success_msg_format,
                        f"[TIMEOUT]: {func.__name__} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS",
                        **msg_kwargs,
                    )

                    return result

                except TimeoutError:
                    alarm(0)

                    msg_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                    }

                    _print_msg(
                        failure_msg_format,
                        f"[TIMEOUT]: {func.__name__} TIMED OUT AFTER {cutoff} SECONDS",
                        **msg_kwargs,
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

                    msg_kwargs = {
                        "name": func.__name__,
                        "cutoff": cutoff,
                    }

                    _print_msg(
                        failure_msg_format,
                        f"[TIMEOUT]: {func.__name__} TIMED OUT AFTER {cutoff} SECONDS",
                        **msg_kwargs,
                    )

                    raise TimeoutError(
                        f"Function {func.__name__} timed out after {cutoff} seconds."
                    )

                # handle unexpected exceptions
                if exc_raised[0]:
                    # pylint: disable=raising-bad-type
                    raise result[0]

                msg_kwargs = {
                    "name": func.__name__,
                    "cutoff": cutoff,
                }

                _print_msg(
                    success_msg_format,
                    f"[TIMEOUT]: {func.__name__} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS",
                    **msg_kwargs,
                )

                return result[0]

            # if somehow not unix or windows, question everything
            raise _UnsupportedOSError(
                "The detected OS is not Unix or Windows."
                + "If this is an unexpected issue, open an issue or send an email."
            )

        return wrapper

    return decorator


def cache():
    """Caches the output of a function and instantly returns it when given the same args and kwargs later."""
    cache_ = {}

    def decorator(func):
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
    """Ensures only one instance of a class can exist at once."""

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
    """Ensures the arguments passed to the function are of the correct type based on the type hints."""

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


def deprecated(reason: str):
    """Decorator to show a function is deprecated.

    :param reason: The reason for deprecation.
    :type reason: str
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# TODO: more logging stuff
# TODO: change to detect calls, and implement a logger to each func
def log_calls(logger=None):
    """Logs function calls using the logger provided.

    :param logger: The logger to use, defaults to None

    :type logger: Logger, optional
    """

    if logger is None:
        logger = getLogger(__name__)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            logger.info(
                "Called %s with args=%s, kwargs=%s, returned %s",
                func.__name__,
                args,
                kwargs,
                result,
            )
            return result

        return wrapper

    return decorator
