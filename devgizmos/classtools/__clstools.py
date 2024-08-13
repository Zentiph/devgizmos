"""
classtools.__decs
-----------------
Module containing decorators for the classtools package.
"""

from functools import wraps
from inspect import getmembers

from ..errguards import ensure_callable, ensure_instance_of


# pylint: disable=invalid-name
class lazyproperty:
    """
    lazyproperty
    ------------
    Transforms the decorated method into a property that is
    only computed once, and is then cached as an attribute.
    """

    def __init__(self, func):
        """
        @lazyproperty
        --------------
        Transforms the decorated method into a property that is
        only computed once, and is then cached as an attribute.

        Example Usage
        ~~~~~~~~~~~~~
        >>> class Circle:
        ...     def __init__(self, radius):
        ...         self.radius = radius
        ...     @lazyproperty
        ...     def area(self):
        ...         print("Computing area")
        ...         return 3.14159 * self.radius**2
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
        for attr_name, attr_value in getmembers(cls):
            if callable(attr_value) and not (
                attr_name.startswith("__") and attr_name.endswith("__")
            ):
                # check if the method is in the class or super classes
                if not any(attr_name in c.__dict__ for c in cls.mro()):
                    continue

                # check if the method should be ignored
                if getattr(attr_value, "_ignore_decoration", False):
                    continue

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
    if not callable(method):
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
    :param cls: The class to make a singleton.
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


class SingleMeta(type):
    """
    SingleMeta
    ----------
    Metaclass that ensures a class is treated as a singleton.

    Example Usage
    ~~~~~~~~~~~~~
    >>> class Singleton(metaclass=SingleMeta):
    ... def __init__(self, x):
    ...     self.x = x
    ...
    >>> obj1 = Singleton(1)
    >>> obj2 = Singleton(2)
    >>>
    >>> obj1.x
    1
    >>> obj2.x
    1
    >>> obj1 is obj2
    True
    """

    __instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance

        return cls.__instances[cls]
