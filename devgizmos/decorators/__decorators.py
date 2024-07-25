# pylint: disable=too-many-lines

"""
decorators.__decorators
=======================
Module containing decorators.
"""

from asyncio import sleep as async_sleep
from collections import OrderedDict
from functools import wraps
from logging import ERROR, INFO, Logger
from time import perf_counter, sleep
from typing import Any, Callable, TypeVar, get_type_hints
from warnings import warn

from ..checks import (
    check_callable,
    check_in_bounds,
    check_subclass,
    check_type,
    check_value,
)

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
LoggingLevel = int


def error_logger(suppress=True, fmt="", logger=None, level=ERROR):
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
    check_type(suppress, bool)
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

                handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)

                if not suppress:
                    raise

                return None

        return wrapper

    return decorator


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


def cache(maxsize=None, *, type_specific=False):
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
    :param type_specific: Whether to cache results differently depending on differently
    typed yet equal parameters, such as func(1) vs func(1.0), defaults to False.
    :type type_specific: bool, optional

    Raises
    ------
    :raises TypeError: If maxsize is not an int or None.
    :raises TypeError: If type_specific is not a bool.
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
    check_type(type_specific, bool)

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


# pylint: disable=invalid-name
class lazy_property:
    """
    lazy_property
    =============
    Transforms the decorated method into a property that is only computed once,
    and is then cached as an attribute.

    Example Usage
    -------------
    ```python
    >>> class Circle:
    ...     def __init__(self, radius):
    ...         self.radius = radius
    ...     @lazy_property
    ...     def area(self):
    ...         print("Computing area")
    ...         return 3.14159 * self.radius ** 2
    ...
    >>> c = Circle(10)
    >>> print(c.area)
    Computing area
    314.159
    >>> print(c.area)
    314.159
    ```
    """

    def __init__(self, func):
        """
        lazy_property
        =============
        Transforms the decorated method into a property that is only computed once,
        and is then cached as an attribute.

        Example Usage
        -------------
        ```python
        >>> class Circle:
        ...     def __init__(self, radius):
        ...         self.radius = radius
        ...     @lazy_property
        ...     def area(self):
        ...         print("Computing area")
        ...         return 3.14159 * self.radius ** 2
        ...
        >>> c = Circle(10)
        >>> print(c.area)
        Computing area
        314.159
        >>> print(c.area)
        314.159
        ```
        """

        self.func = func
        self.__doc__ = getattr(func, "__doc__")
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.name, value)
        return value


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
    ...         self.a = a
    ...     def __repr__(self):
    ...         return f"MyClass(a={self.a})"
    ...     def add_to_a(self, x):
    ...         self.a += x
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


def immutable(cls):
    """
    immutable
    =========
    Enforces immutability onto the decorated object.

    Raises
    ------
    :raises AttributeError: If an attempt is made to edit the immutable object's attributes.

    Example Usage
    -------------
    ```python
    >>> @immutable
    ... class Point2D:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> pt = Point2D(3, 5)
    >>> pt.x = 2
    AttributeError: Cannot modify attribute 'x' of immutable instance
    ```
    """

    class ImmutableInstance(cls):
        """
        ImmutableInstance
        =================
        Copies the decorated class and makes it immutable.
        """

        __is_frozen = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__is_frozen = True

        def __setattr__(self, key, value):
            if self.__is_frozen:
                raise AttributeError(
                    f"Cannot modify attribute '{key}' of immutable instance"
                )
            super().__setattr__(key, value)

    return ImmutableInstance


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
    ...         self.x = x
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
