"""
codeutils.__cutils
==================
Module containing function inspection/controlling utility.
"""

from abc import ABC, abstractmethod
from functools import wraps
from inspect import currentframe
from platform import system

from ..checks import (
    check_callable,
    check_in_bounds,
    check_no_duplicates,
    check_subclass,
    check_type,
)

if system() in ("Darwin", "Linux"):
    # pylint: disable=no-name-in-module
    from signal import SIGALRM, alarm, signal  # type: ignore
elif system() == "Windows":
    # pylint: disable=no-name-in-module
    from threading import Thread  # type: ignore


class UnsupportedOSError(Exception):
    """
    UnsupportedOSError
    ==================
    Error to raise when an unsupported OS is being used.
    Primary purpose is as a "catch all cases" solution, as it is unlikely this will ever be needed.
    """


class Timeout:
    """Class for timing out code if it takes too long to run."""

    def __init__(self, cutoff, exc=TimeoutError):
        """
        Timeout
        =======
        Class for timing out code if it takes too long to run.
        Can be used as a context manager and a decorator.

        Parameters
        ----------
        :param cutoff: The time allotted for the code to run in seconds.
        :type cutoff: int | float
        :param exc: The exception to raise if time runs out, or None, defaults to TimeoutError.
        :type exc: Type[BaseException] | None

        Raises
        ------
        :raises TypeError: If cutoff is not an int or float.
        :raises TypeError: If exc is not a BaseException or None.
        :raises ValueError: If cutoff is less than or equal to 0.

        Example Usage (Context Manager)
        -------------------------------
        ```python

        ```

        Example Usage (Decorator)
        -------------------------
        ```python

        ```
        """

        # type checks
        check_type(cutoff, (int, float))
        check_subclass(BaseException, exc)

        # value checks
        check_in_bounds(cutoff, 0, None, inclusive=False)

        self.__cutoff = cutoff
        self.__exc = exc
        if system() in ("Darwin", "Linux"):
            self.__sys = "Unix"
        elif system() == "Windows":
            self.__sys = "Windows"
        else:
            raise UnsupportedOSError(
                "System being used is not 'Darwin', 'Linux', or 'Windows'."
            )

    def __enter__(self):
        if self.__sys == "Windows":
            raise UnsupportedOSError(
                "Windows systems cannot use Timeout as a context manager."
            )

        def handler():
            raise self.__exc(
                f"Code starting at line {currentframe().f_back.f_lineno} timed out after {self.__cutoff} seconds."
            )

        signal(SIGALRM, handler)
        alarm(self.__cutoff)

        yield

    def __exit__(self, type_, value, traceback):
        if self.__sys == "Windows":
            raise UnsupportedOSError(
                "Windows systems cannot use Timeout as a context manager."
            )

        alarm(0)

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Unix implementation
            if self.__sys == "Unix":
                with self:
                    return func(*args, **kwargs)

            # Windows implementation
            # initialize as lists to allow for modification in nests
            result = [None]
            exc_info = [Exception, False]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exc_info[0], exc_info[1] = e, True

            thread = Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(self.__cutoff)
            if thread.is_alive():
                thread.join()

                raise self.__exc(
                    f"Func {func.__name__} at line {currentframe().f_back.f_lineno} "
                    + f"timed out after {self.__cutoff} seconds."
                )

            if exc_info[1]:
                raise exc_info[0]

            return result[0]

        return wrapper

    @property
    def cutoff(self):
        """
        Timeout.cutoff
        ==============
        Returns the cutoff time of Timeout.

        Return
        ------
        :return: The cutoff time.
        :rtype: int | float
        """

        return self.__cutoff

    @property
    def exc(self):
        """
        Timeout.exc
        ===========
        Returns the exception that will be raised by Timeout if its cutoff time is exceeded.

        Return
        ------
        :return: The exception raised when the cutoff time is exceeded.
        :rtype: Type[BaseException]
        """

        return self.__exc

    @exc.setter
    def exc(self, e, /):
        """
        Timeout.exc()
        =============
        Sets Timeout's exception that will be raised if the cutoff time is exceeded.

        Parameters
        ----------
        :param e: The new exception.
        :type e: Type[BaseException]

        Raises
        ------
        :raises TypeError: If e is not an instance of BaseException.
        """

        # type checks
        check_subclass(BaseException, e)

        self.__exc = e


class FailureHandler(ABC):
    """Abstract base class for FailureManager handlers."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.__priority = 1
        self.__returned = None
        self.__suppress = True

    @abstractmethod
    def __call__(self):
        pass

    @property
    def priority(self):
        """
        FailureHandler.priority
        =======================
        Returns the FailureHandler's priority.
        Priority determines the order the FailureManager executes its handlers.
        Lowest number (minimum 1) takes highest priority.

        Return
        ------
        :return: The priority.
        :rtype: int
        """

        return self.__priority

    @priority.setter
    def priority(self, p, /):
        """
        FailureHandler.priority()
        =========================
        Sets the FailureHandler's priority.
        Priority determines the order the FailureManager executes its handlers.
        Lowest number (minimum 1) takes highest priority.

        Parameters
        ----------
        :param p: The priority of the handler.
        :type p: int

        Raises
        ------
        :raises TypeError: If p is not an int.
        :raises ValueError: If p is less than or equal to 0.
        """

        # type checks
        check_type(p, int)

        # value checks
        check_in_bounds(p, 1, None)

        self.__priority = p

    @property
    def returned(self):
        """
        FailureHandler.returned
        =======================
        Returns the return value when called due to an error being raised.

        Return
        ------
        :return: The return value.
        :rtype: Any
        """

        return self.__returned

    @property
    def suppress(self):
        """
        FailureHandler.suppress
        =======================
        Returns whether the handler should suppress exceptions.

        Return
        ------
        :return: Whether the handler should suppress exceptions.
        :rtype: bool
        """

        return self.__suppress

    @suppress.setter
    def suppress(self, s):
        """
        FailureHandler.suppress()
        =========================
        Sets whether the FailureHandler should suppress exceptions.

        Parameters
        ----------
        :param s: Whether to suppress exceptions.
        :type s: bool
        """

        # type checks
        check_type(s, bool)

        self.__suppress = s

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Fallback(FailureHandler):
    """FailureHandler for FailureManager that falls back to a function if the code fails."""

    def __init__(self, func, *args, **kwargs):
        """
        Fallback
        ========
        FailureHandler for FailureManager that executes the given
        func with the given args and kwargs if the code fails.
        Meant to be passed to FailureManager as an argument, not
        to be used as a standalone handler.

        Parameters
        ----------
        :param func: The fallback function.
        :type func: Callable[..., Any]
        :param args: The args to pass to func.
        :type args: Any
        :param kwargs: The kwargs to pass to func.
        :type kwargs: Dict[str, Any]

        Raises
        ------
        :raises TypeError: If func is not callable.

        Example Usage
        -------------
        ```python
        # TODO:
        ```
        """

        # type checks
        check_callable(func)

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
        ===================
        Verifies the function, args, and kwargs
        passed to Fallback will run and not raise errors.
        If the function involves randomness, this result cannot be trusted.

        Return
        ------
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
        =============================
        Returns the priorities of each handler.

        Return
        ------
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


# TODO: add an auto-sorting/changing priority arg called "set_priorities"
# it will automatically find the next available priority and assign that to the handlers
# in a first come first serve pattern
class FailureManager:
    """Class for handling code failures."""

    def __init__(self, *handlers, exceptions=(Exception,)):
        """
        FailureManager
        ==============
        Class that handles code failures using the handler provided.
        Can be used as a context manager and a decorator.

        Parameters
        ----------
        :param handlers: The handlers to use when handling failures, or None for no handler, defaults to None.
        :type handlers: Tuple[FailureHandler, ...] | None, optional
        :param exceptions: The exceptions to activate the FailureManager for.
        :type exceptions: Tuple[Type[BaseException], ...]

        Raises
        ------
        :raises TypeError: If handlers is not a Tuple of FailureHandler instances or None.
        :raises TypeError: If exceptions is not a Tuple of BaseException instances.

        Example Usage (Context Manager)
        -------------------------------
        ```python
        # TODO:
        ```

        Example Usage (Decorator)
        -------------------------
        ```python
        # TODO:
        ```
        """

        # type checks
        if handlers is not None:
            check_type(handlers, tuple)
            check_subclass(FailureHandler, tuple(type(h) for h in handlers))
        check_type(exceptions, tuple)
        check_subclass(BaseException, exceptions)

        self.__handlers = list(handlers)
        self.__sort_handlers()
        self.__exceptions = exceptions
        self.__caught = []

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if check_type(value, self.__exceptions, raise_exc=False) and self.handlers:

            for handler in self.__handlers:
                handler()

                if not handler.suppress:
                    return False

            self.__caught.append((type_, value, traceback))

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
        ================================
        Internal class func for sorting the handlers.
        """

        self.__handlers.sort(key=lambda h: h.priority)

        priorities = tuple(h.priority for h in self.__handlers)
        check_no_duplicates(
            priorities,
            exc_msg="FailureManager cannot contain two handlers with the same priority",
        )

    def add_handler(self, handler, /):
        """
        FailureManager.add_handler()
        ============================
        Adds a handler to the FailureManager.

        Parameters
        ----------
        :param handler: The handler to add.
        :type handler: FailureHandler
        """

        # type checks
        check_subclass(FailureHandler, type(handler))

        self.__handlers.append(handler)
        self.__sort_handlers()

    def del_handler(self, priority, /):
        """
        FailureManager.del_handler()
        ============================
        Removes the handler with the given priority from the FailureManager.

        Parameters
        ----------
        :param priority: The priority of the handler to remove.
        :type priority: int
        """

        self.__handlers.pop(priority - 1)

    @property
    def handlers(self):
        """
        FailureManager.handlers
        =======================
        Returns a tuple of the FailureManager's handlers.

        Return
        ------
        :return: A tuple of the handlers.
        :rtype: Tuple[FailureHandler, ...] | None
        """

        return _HandlerCollection(*self.__handlers)

    @property
    def exceptions(self):
        """
        FailureManager.exceptions
        =========================
        Returns the exceptions being watched for by the FailureManager.

        Return
        ------
        :return: The exceptions being watched for.
        :rtype: Tuple[Type[BaseException], ...]
        """

        return self.__exceptions

    @exceptions.setter
    def exceptions(self, excs):
        """
        FailureManager.exceptions()
        ===========================
        Sets the exceptions for the FailureManager to watch.

        Parameters
        ----------
        :param excs: The exceptions to watch for.
        :type excs: Tuple[Type[BaseException], ...]

        Raises
        ------
        :raises TypeError: If excs is not a Tuple of BaseException instances.
        """

        # type checks
        check_type(excs, tuple)
        check_subclass(BaseException, excs)

        self.__exceptions = excs

    @property
    def caught(self):
        """
        FailureManager.caught
        =====================
        Returns the info of the exceptions caught by FailureManager in chronological order.
        For the most recent caught exception, get FailureManager.caught[-1].

        Return
        ------
        :return: The info of the caught exceptions (type, value, traceback).
        :rtype: List[Tuple[Type[BaseException], BaseException, TracebackType]]
        """

        return self.__caught
