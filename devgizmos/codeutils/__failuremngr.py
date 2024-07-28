# pylint: disable=too-many-lines

"""
codeutils.__cutils
==================
Module containing function inspection/controlling utility.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps

from ..errguards import (
    ensure_callable,
    ensure_in_bounds,
    ensure_instance_of,
    ensure_no_duplicates,
    ensure_superclass_of,
)


class FailureHandler(ABC):
    """Abstract base class for FailureManager handlers."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.__priority = 1
        self.__returned = None
        self.__suppress = True
        self.__on = True

    @abstractmethod
    def __call__(self):
        pass

    @property
    def activated(self):
        """
        FailureHandler.activated
        ------------------------
        Returns whether the FailureHandler is activated.

        Return
        ~~~~~~
        :return: Whether the FailureHandler is activated.
        :rtype: bool
        """

        return self.__on

    @activated.setter
    def activated(self, a, /):
        """
        FailureHandler.activated()
        --------------------------
        Sets whether the FailureHandler is activated.

        Parameters
        ~~~~~~~~~~
        :param a: Whether the FailureHandler is activated.
        :type a: bool

        Raises
        ~~~~~~
        :raises TypeError: If a is not a bool.
        """

        # type checks
        ensure_instance_of(a, bool)

        self.__on = a

    @property
    def priority(self):
        """
        FailureHandler.priority
        -----------------------
        Returns the FailureHandler's priority.
        Priority determines the order the FailureManager executes its handlers.
        Lowest number (minimum 1) takes highest priority.

        Return
        ~~~~~~
        :return: The priority.
        :rtype: int
        """

        return self.__priority

    @priority.setter
    def priority(self, p, /):
        """
        FailureHandler.priority()
        -------------------------
        Sets the FailureHandler's priority.
        Priority determines the order the FailureManager executes its handlers.
        Lowest number (minimum 1) takes highest priority.

        Parameters
        ~~~~~~~~~~
        :param p: The priority of the handler.
        :type p: int

        Raises
        ~~~~~~
        :raises TypeError: If p is not an int.
        :raises ValueError: If p is less than or equal to 0.
        """

        # type checks
        ensure_instance_of(p, int)

        # value checks
        ensure_in_bounds(p, 1, None)

        self.__priority = p

    @property
    def returned(self):
        """
        FailureHandler.returned
        -----------------------
        Returns the return value when called due to an error being raised.

        Return
        ~~~~~~
        :return: The return value.
        :rtype: Any
        """

        return self.__returned

    @property
    def suppress(self):
        """
        FailureHandler.suppress
        -----------------------
        Returns whether the handler should suppress exceptions.

        Return
        ~~~~~~
        :return: Whether exceptions should be suppressed.
        :rtype: bool
        """

        return self.__suppress

    @suppress.setter
    def suppress(self, s):
        """
        FailureHandler.suppress()
        -------------------------
        Sets whether exceptions should be suppressed by the handler.

        Parameters
        ~~~~~~~~~~
        :param s: Whether to suppress exceptions.
        :type s: bool
        """

        # type checks
        ensure_instance_of(s, bool)

        self.__suppress = s

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


# empty shell of a class, but exists merely for
# suppressing functionality without any other functionality
class Suppress(FailureHandler):
    """FailureHandler for FailureManager that suppresses the exceptions given to FailureManager."""

    def __init__(self):
        """
        Suppress
        --------
        FailureHandler for FailureManager that suppresses any exceptions
        the FailureManager is listening for.

        Example Usage
        ~~~~~~~~~~~~~
        >>> # TODO
        """

        super().__init__()

    def __call__(self):
        return

    def __str__(self):
        return "Suppress()"

    def __repr__(self):
        return "Suppress()"


class Fallback(FailureHandler):
    """FailureHandler for FailureManager that falls back to a function if the code fails."""

    def __init__(self, func, *args, **kwargs):
        """
        Fallback
        --------
        FailureHandler for FailureManager that executes the given
        func with the given args and kwargs if the code fails.
        Meant to be passed to FailureManager as an argument, not
        to be used as a standalone handler.

        Parameters
        ~~~~~~~~~~
        :param func: The fallback function.
        :type func: Callable[..., Any]
        :param args: The args to pass to func.
        :type args: Any
        :param kwargs: The kwargs to pass to func.
        :type kwargs: Dict[str, Any]

        Raises
        ~~~~~~
        :raises TypeError: If func is not callable.

        Example Usage
        ~~~~~~~~~~~~~
        >>> # TODO
        >>>
        >>> # showcasing Fallback's unique 'validate' and 'error_scan' methods
        >>> def fun():
        ...     print("falling back")
        ...
        >>> fb = Fallback(fun)
        >>> # validate that the fallback func works
        >>> fb.validate()
        falling back
        True
        >>>
        >>> def risky():
        ...     raise TypeError
        ...
        >>> fb2 = Fallback(risky)
        >>> fb2.validate()
        False
        >>>
        >>> # error_scan works the same as validate but returns error info
        >>> fb.error_scan()
        >>> # returned None
        >>> fb2.error_scan()
        TypeError()
        """

        # type checks
        ensure_callable(func)

        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
        super().__init__()

    def __call__(self):
        self.__returned = self.__func(*self.__args, **self.__kwargs)
        return self.__returned

    def validate(self):
        """
        Fallback.validate()
        -------------------
        Verifies the function, args, and kwargs
        passed to Fallback will run and not raise errors.
        If the function involves randomness, this result cannot be trusted.

        Return
        ~~~~~~
        :return: Whether the function raised an exception.
        :rtype: bool
        """

        try:
            self.__func(*self.__args, **self.__kwargs)
            return True
        except Exception:
            return False

    def error_scan(self):
        """
        Fallback.error_scan()
        ---------------------
        Works identically to Fallback.validate(), but returns error info instead.

        Return
        ~~~~~~
        :return: Either None if the function raised no errors,
        or the exception that was raised when running the function.
        :rtype: Type[Exception] | None
        """

        try:
            self.__func(*self.__args, **self.__kwargs)
            return None
        except Exception as e:
            return e

    def __str__(self):
        return f"Fallback({self.__func.__name__}, {self.__args}, {self.__kwargs})"

    def __repr__(self):
        return f"Fallback({self.__func.__name__}, {self.__args}, {self.__kwargs})"


class _HandlerCollection:
    """
    Helper class to provide additional functionality
    to the FailureManager.handlers property.
    """

    def __init__(self, *handlers):
        self.__handlers = handlers

    @property
    def priorities(self):
        """
        _HandlerCollection.priorities
        -----------------------------
        Returns the priorities of each handler.

        Return
        ~~~~~~
        :return: The priorities of each handler.
        :rtype: Tuple[int, ...]
        """
        return tuple(handler.priority for handler in self.__handlers)

    def __iter__(self):
        return iter(self.__handlers)

    def __len__(self):
        return len(self.__handlers)

    def __getitem__(self, index):
        return self.__handlers[index]

    def __str__(self):
        return repr(self.__handlers)

    def __repr__(self):
        return repr(self.__handlers)


class _ExcData:
    """Helper class for returning caught exception data with FailureManager."""

    def __init__(self, type_, value, traceback, time):
        self.__type = type_
        self.__value = value
        self.__trace = traceback
        self.__time = time

    @property
    def type(self):
        """
        _ExcData.type
        -------------
        Returns the exception type.
        """

        return self.__type

    @property
    def value(self):
        """
        _ExcData.value
        --------------
        Returns the exception value.
        """

        return self.__value

    @property
    def traceback(self):
        """
        _ExcData.traceback
        ------------------
        Returns the exception traceback.
        """

        return self.__trace

    @property
    def time(self):
        """
        _ExcData.time
        -------------
        Returns the time the exception occurred.
        """

        return self.__time

    def reraise(self):
        """
        _ExcData.reraise
        ----------------
        Re-raises the caught exception.
        """

        raise self.__value

    def __str__(self):
        return (
            f"Exception data: type={self.__type}, "
            + f"value={repr(self.__value)}, traceback={self.__trace}, time={self.__time}"
        )

    def __repr__(self):
        return (
            f"Exception data: type={self.__type}, "
            + f"value={repr(self.__value)}, traceback={self.__trace}, time={self.__time}"
        )


class FailureManager:
    """Class for handling code failures."""

    def __init__(self, *handlers, exceptions=(Exception,)):
        """
        FailureManager
        --------------
        Class that handles code failures using the handler provided.
        Can be used as a context manager and a decorator.

        Parameters
        ~~~~~~~~~~
        :param handlers: The handlers to use when handling failures, or None for no handler, defaults to None.
        :type handlers: Tuple[FailureHandler, ...] | None, optional
        :param exceptions: The exceptions to activate the FailureManager for, defaults to (Exception,).
        :type exceptions: Tuple[Type[BaseException], ...], optional

        Raises
        ~~~~~~
        :raises TypeError: If handlers is not a Tuple of FailureHandler instances or None.
        :raises TypeError: If exceptions is not a Tuple of BaseExceptions.

        Example Usage
        ~~~~~~~~~~~~~
        >>> # TODO
        """

        # type checks
        if handlers is not None:
            ensure_instance_of(handlers, tuple)
            ensure_superclass_of(FailureHandler, tuple(type(h) for h in handlers))
        ensure_instance_of(exceptions, tuple)
        ensure_superclass_of(BaseException, exceptions)

        self.__handlers = list(handlers)
        self.__sort_handlers()
        self.__exceptions = exceptions
        self.__caught = []

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if isinstance(value, self.__exceptions) and self.handlers:

            for handler in self.__handlers:
                if handler.activated:
                    handler()

                    if not handler.suppress:
                        return False

            self.__caught.append(_ExcData(type_, value, traceback, datetime.now()))

            return True
        return False

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __sort_handlers(self):
        """
        FailureManager.__sort_handlers()
        --------------------------------
        Internal class func for sorting the handlers.
        """

        self.__handlers.sort(key=lambda h: h.priority)

        priorities = tuple(h.priority for h in self.__handlers)
        ensure_no_duplicates(
            priorities,
            msg="FailureManager cannot contain two handlers with the same priority",
        )

    def sort_handler_priorities(self):
        """
        FailureManager.sort_handler_priorities()
        ----------------------------------------
        Sorts the priorities of the handlers. Handlers with the highest priorities are pushed to the top first.
        Ex: Handlers with priorities of h1: 2, h2: 4, h3: 7 -> h1: 1, h2: 2, h3: 3
        """

        # this should work assuming the handlers are already sorted due to
        # self.__sort_handlers call in __init__
        for i, handler in enumerate(self.__handlers):
            if i + 1 not in self.handlers.priorities:
                handler.priority = i + 1

    def set_priority(self, handler, priority, /):
        """
        FailureManager.set_priority()
        -----------------------------
        Sets the priority of the specified handler object.

        Parameters
        ~~~~~~~~~~
        :param handler: The handler to change the priority of.
        :type handler: FailureHandler
        :param priority: The new priority.
        :type priority: int
        """

        # type checks
        ensure_superclass_of(FailureHandler, type(handler))
        ensure_instance_of(priority, int)

        # value checks
        ensure_in_bounds(priority, 1, None)

        try:
            self.__handlers.index(handler)
        except ValueError as e:
            raise f"'{handler}' not found in the FailureManager" from e

        handler.priority = priority

        self.__sort_handlers()

    def add_handler(self, handler, /):
        """
        FailureManager.add_handler()
        ----------------------------
        Adds a handler to the FailureManager.

        Parameters
        ~~~~~~~~~~
        :param handler: The handler to add.
        :type handler: FailureHandler
        """

        # type checks
        ensure_superclass_of(FailureHandler, type(handler))

        self.__handlers.append(handler)
        self.__sort_handlers()

    def del_handler(self, priority, /):
        """
        FailureManager.del_handler()
        ----------------------------
        Removes the handler with the given priority from the FailureManager.

        Parameters
        ~~~~~~~~~~
        :param priority: The priority of the handler to remove.
        :type priority: int
        """

        self.__handlers.pop(priority - 1)

    @property
    def handlers(self):
        """
        FailureManager.handlers
        -----------------------
        Returns a tuple of the FailureManager's handlers.

        Return
        ~~~~~~
        :return: A tuple of the handlers.
        :rtype: Tuple[FailureHandler, ...] | None
        """

        return _HandlerCollection(*self.__handlers)

    @property
    def exceptions(self):
        """
        FailureManager.exceptions
        -------------------------
        Returns the exceptions being watched for by the FailureManager.

        Return
        ~~~~~~
        :return: The exceptions being watched for.
        :rtype: Tuple[Type[BaseException], ...]
        """

        return self.__exceptions

    @exceptions.setter
    def exceptions(self, excs):
        """
        FailureManager.exceptions()
        ---------------------------
        Sets the exceptions for the FailureManager to watch.

        Parameters
        ~~~~~~~~~~
        :param excs: The exceptions to watch for.
        :type excs: Tuple[Type[BaseException], ...]

        Raises
        ~~~~~~
        :raises TypeError: If excs is not a Tuple of BaseExceptions.
        """

        # type checks
        ensure_instance_of(excs, tuple)
        ensure_superclass_of(BaseException, excs)

        self.__exceptions = excs

    @property
    def caught(self):
        """
        FailureManager.caught
        ---------------------
        Returns the info of the exceptions caught by FailureManager in chronological order.
        For the most recent caught exception, get FailureManager.caught[-1].

        Return
        ~~~~~~
        :return: The info of the caught exceptions (type, value, traceback, datetime).
        :rtype: List[_ExcData]
        """

        return self.__caught

    def clear_caught(self):
        """
        FailureManager.clear_caught()
        -----------------------------
        Clears the list of caught exceptions.
        """

        self.__caught.clear()
