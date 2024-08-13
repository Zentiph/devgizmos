"""
funcutils.__fnutils
-------------------
Module containing utility for working with functions.
"""

from collections import OrderedDict
from functools import wraps
from time import perf_counter, sleep
from typing import get_type_hints
from warnings import warn

from ..errguards import ensure_callable, ensure_in_bounds, ensure_instance_of


def rate_limit(*args):
    """
    @rate_limit()
    -------------
    Limits the number of times a function can be called in the given period.

    Parameters
    ~~~~~~~~~~
    :param interval: The time interval between each call (single argument).
    :type interval: int | float
    :param calls: The number of allowed calls in the period (first of two arguments).
    :type calls: int
    :param period: The time period in seconds (second of two arguments).
    :type period: int | float

    Raises
    ~~~~~~
    :raises TypeError: If any number of args other than 1 or 2 are passed.
    :raises TypeError: If interval is not an int or float.
    :raises TypeError: If calls is not an int.
    :raises TypeError: If period if not an int or float.
    :raises ValueError: If interval is 0 or less.
    :raises ValueError: If calls is 0 or less.
    :raises ValueError: If period is 0 or less.

    Return
    ~~~~~~
    :return: The decorated function.
    :rtype: Decorated

    Example Usage
    ~~~~~~~~~~~~~
    >>> from time import perf_counter
    >>>
    >>> @rate_limit(1)
    ... def get_time():
    ...     return perf_counter()
    ...
    >>> t1 = get_time()
    >>> t2 = get_time()
    >>> t2 - t1
    1.0003656
    >>> # the function will not be re-called
    >>> # for ~1 second each time it is called
    """

    last_called = [0.0]

    # determine interval based off args length
    # or raise an exception if too many/little args
    if len(args) == 1:
        # type checks
        ensure_instance_of(args[0], int, float)

        # value checks
        ensure_in_bounds(args[0], 0, None, inclusive=False)

        interval = args[0]
    elif len(args) == 2:
        # type checks
        ensure_instance_of(args[0], int)
        ensure_instance_of(args[1], int, float)

        # value checks
        ensure_in_bounds(args[0], 1, None)
        ensure_in_bounds(args[1], 0, None, inclusive=False)

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


def cache(maxsize=None, /, *, type_specific=False):
    """
    @cache()
    --------
    Caches the output of the decorated function and instantly returns it
    when given the same args and kwargs later.
    Uses LRU caching if a maxsize is provided.

    Parameters
    ~~~~~~~~~~
    :param maxsize: The maximum number of results to store in the cache using an LRU system, defaults to None.
    :type maxsize: int | None, optional
    :param type_specific: Whether to cache results differently depending on differently
    typed yet equal parameters, such as func(1) vs func(1.0), defaults to False.
    :type type_specific: bool, optional

    Raises
    ~~~~~~
    :raises TypeError: If maxsize is not an int or None.
    :raises TypeError: If type_specific is not a bool.
    :raises ValueError: If maxsize is less than 1.

    Return
    ~~~~~~
    :return: The decorated function.
    :rtype: Decorated

    Example Usage
    ~~~~~~~~~~~~~
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
    """

    ensure_instance_of(maxsize, int, optional=True)
    ensure_instance_of(type_specific, bool)
    if maxsize is not None:
        ensure_in_bounds(maxsize, 1, None)

    def decorator(func):
        cache_ = OrderedDict()

        @wraps(func)
        def wrapper(*args, **kwargs):
            if type_specific:
                key = (
                    tuple((type(arg), arg) for arg in args),
                    tuple((type(v), k, v) for k, v in kwargs.items()),
                )
            else:
                key = (args, tuple(kwargs.items()))

            if key in cache_:
                cache_.move_to_end(key)
                return cache_[key]

            result = func(*args, **kwargs)

            if maxsize is not None and len(cache_) >= maxsize:
                cache_.popitem(last=False)

            cache_[key] = result
            return result

        return wrapper

    return decorator


def deprecated(reason, version=None, date=None):
    """
    @deprecated()
    -------------
    Creates a DeprecationWarning to show the decorated function or class is deprecated.

    Parameters
    ~~~~~~~~~~
    :param reason: The reason for deprecation.
    :type reason: str
    :param version: The version number of the function, defaults to None.
    :type version: int | float | str | None, optional
    :param date: The date of removal.
    :type date: str | None, optional

    Raises
    ~~~~~~
    :raises TypeError: If reason is not a str.
    :raises TypeError: If version is not an int, float, str, or None.
    :raises TypeError: If date is not a str or None.

    Return
    ~~~~~~
    :return: The decorated function.
    :rtype: Decorated

    Example Usage
    ~~~~~~~~~~~~~
    >>> @deprecated("We found a better way to do this", "v1.0.3")
    ... def old_func(*args, **kwargs):
    ...     return all(args)
    ...
    >>> old_func(1, 2)
    <stdin>:1: DeprecationWarning: old_func is deprecated: We found a better way to do this (Ver: v1.0.3)
    True
    """

    # type checks
    ensure_instance_of(reason, str)
    ensure_instance_of(version, int, float, str, optional=True)
    ensure_instance_of(date, str, optional=True)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated: {reason}"
            if version:
                msg += f" | Ver: {version}"
            if date:
                msg += f" | Removal: {date}"

            warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def enforce_type_hints(func):
    """
    @enforce_type_hints
    -------------------
    Ensures the arguments passed to the decorated function are of the correct type based on the type hints.

    Parameters
    ~~~~~~~~~~
    :param func: The function to decorate and type check.
    :type func: Callable[P, T]

    Raises
    ~~~~~~
    :raises TypeError: If the args or kwargs passed do not match the function's type hints.
    :raises TypeError: If the return value does not match the function's type hints.

    Return
    ~~~~~~
    :return: The decorated function.
    :rtype: Callable[P, T]

    Example Usage
    ~~~~~~~~~~~~~
    >>> @enforce_type_hints
    ... def typed_fun(a: int, b: float) -> str:
    ...     return str(a + b)
    ...
    >>> typed_fun(2, 1.0)
    '3.0'
    >>> typed_fun(3.2, 5)
    TypeError: Argument 'a' must be type 'int'
    """

    # type checks
    ensure_callable(func)

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
            raise TypeError(f"Return value must be type '{hints['return'].__name__}'")
        return result

    return wrapper
