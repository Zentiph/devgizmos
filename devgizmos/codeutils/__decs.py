"""
codeutils.__decs
================
Module containing decorators for the codeutils package.
"""

from collections import OrderedDict
from functools import wraps
from inspect import ismethod
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
    >>> # the function will not be "re-callable"
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


# pylint: disable=invalid-name
class lazy_property:
    """
    Transforms the decorated method into a property that is
    only computed once, and is then cached as an attribute.
    """

    def __init__(self, func):
        """
        @lazy_property
        --------------
        Transforms the decorated method into a property that is
        only computed once, and is then cached as an attribute.

        Example Usage
        ~~~~~~~~~~~~~
        >>> class Circle:
        ...     def __init__(self, radius):
        ...         self.radius = radius
        ...     @lazy_property
        ...     def area(self):
        ...         print("Computing area")
        ...         return 3.14159 * self.radius ** 2
        ...
        >>> c = Circle(10)
        >>> c.area
        Computing area
        314.159
        >>> c.area
        314.159
        """

        ensure_callable(func)

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
    ensure_instance_of(version, (int, float, str), optional=True)
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


def decorate_all_methods(decorator, *args, **kwargs):
    """
    @decorate_all_methods()
    -----------------------
    Decorates all the methods in a class with the given decorator,
    ignoring magic/dunder methods.

    Parameters
    ~~~~~~~~~~
    :param decorator: The decorator to apply to each method.
    :type decorator: Decorator
    :param args: The arguments passed to the decorator.
    :type args: Any
    :param kwargs: The keyword arguments passed to the decorator.
    :type kwargs: Any

    Raises
    ~~~~~~
    :raises TypeError: If decorator is not callable.

    Return
    ~~~~~~
    :return: The decorated class.
    :rtype: DecoratedCls

    Example Usage
    ~~~~~~~~~~~~~
    >>> @decorate_all_methods(deprecated, "Don't use this class anymore, see MyBetterClass")
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
    <stdin>:1: DeprecationWarning: add_to_a is deprecated: Don't use this class anymore, see MyBetterClass
    """

    # type checks
    ensure_callable(decorator)

    def decorator_(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not (
                attr_name.startswith("__") and attr_name.endswith("__")
            ):
                # check if the method should be ignored
                if getattr(attr_value, "_ignore_decoration", False):
                    # try to use the decorator assuming it contains
                    # a decorator and wrapper function
                    try:
                        attr_value = decorator(*args, **kwargs)(attr_value)

                    # if above fails, try to use the decorator
                    # assuming it only contains a wrapper
                    except TypeError:
                        attr_value = decorator(attr_value, *args, **kwargs)

                    setattr(cls, attr_name, attr_value)

        return cls

    return decorator_


def ignore_method_decoration(method, /):
    """
    @ignore_method_decoration
    -------------------------
    Decorator that marks the decorated method to be
    ignored by the decorate_all_methods decorator.

    Parameters
    ~~~~~~~~~~
    :param method: The method to decorate.
    :type method: Callable[..., Any]

    Raises
    ~~~~~~
    :raises TypeError: If method is not a method of a class.

    Return
    ~~~~~~
    :return: The decorated method.
    :rtype: Decorated

    Example Usage
    ~~~~~~~~~~~~~
    >>> @decorate_all_methods(deprecated, "Don't use this class anymore, see MyBetterClass")
    ... class MyClass:
    ...     def __init__(self, a):
    ...         self.a = a
    ...     def __repr__(self):
    ...         return f"MyClass(a={self.a})"
    ...     def add_to_a(self, x):
    ...         self.a += x
    ...     @ignore_method_decoration
    ...     def subtract_from_a(self, x):
    ...         self.a -= x
    ...
    >>> cls = MyClass(1)
    >>> cls.add_to_a(2)
    <stdin>:1: DeprecationWarning: add_to_a is deprecated: Don't use this class anymore, see MyBetterClass
    >>> cls.subtract_from_a(2)
    >>> # no deprecation warning
    """

    # type checks
    if not ismethod(method):
        raise TypeError(f"expected a method, got {type(method).__name__} instead")

    method._ignore_decoration = True  # pylint: disable=protected-access
    return method


def immutable(cls):
    """
    @immutable
    ----------
    Enforces immutability onto the decorated object.

    Parameters
    ~~~~~~~~~~
    :param cls: The class to decorate and make immutable.
    :type cls: Type[T]

    Raises
    ~~~~~~
    :raises AttributeError: If an attempt is made to edit the immutable object's attributes.

    Return
    ~~~~~~
    :return: The decorated class.
    :rtype: ImmutableInstance

    Example Usage
    ~~~~~~~~~~~~~
    >>> @immutable
    ... class Point2D:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> pt = Point2D(3, 5)
    >>> pt.x = 2
    AttributeError: Cannot modify attribute 'x' of immutable instance
    """

    # type checks
    ensure_instance_of(cls, type)

    class ImmutableInstance(cls):
        """
        ImmutableInstance
        -----------------
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


def singleton(cls):
    """
    @singleton
    ----------
    Ensures only one instance of a class can exist at once.

    Parameters
    ~~~~~~~~~~
    :param cls: The class to decorate and make a singleton.
    :type cls: Type[T]

    Return
    ~~~~~~
    :return: The decorated class.
    :rtype: DecoratedCls

    Example Usage
    ~~~~~~~~~~~~~
    >>> @singleton
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
    """

    # type checks
    ensure_instance_of(cls, type)

    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def type_checker(func):
    """
    @type_checker
    -------------
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
    >>> @type_checker
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
