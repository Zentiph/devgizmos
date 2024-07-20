"""
codeutils.__cutils
==================
Module containing function inspection/controlling utility.
"""

from abc import abstractmethod
from functools import wraps
from inspect import currentframe
from platform import system
from typing import Protocol

from ..checks import check_callable, check_in_bounds, check_subclass, check_type

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


class BaseFailureHandler(Protocol):
    """Base class for FailureManager handlers."""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self):
        pass


class FailureManager:
    """Class for handling code failures."""

    def __init__(self, handler=None, exceptions=(Exception,)):
        """
        FailureManager
        ==============
        Class that handles code failures using the handler provided.

        :param handler: The handler to use when handling failures, or None for no handler, defaults to None
        :type handler: FailureHandler, optional
        :param exceptions: The exceptions to activate the FailureManager for.
        :type exceptions: Tuple[Type[BaseException], ...]
        """

        # type checks
        check_subclass(BaseFailureHandler, handler)
        check_type(exceptions, tuple)
        check_subclass(BaseException, exceptions)

        self.__handler = handler
        self.__exceptions = exceptions

    @property
    def handler(self):
        """
        FailureManager.handler
        ======================
        Returns the FailureManager's handler.

        Return
        ------
        :return: The handler.
        :rtype: BaseFailureHandler
        """

        return self.__handler

    @handler.setter
    def handler(self, h, /):
        """
        FailureManager.handler()
        ========================
        Sets the FailureManager's handler.

        Parameters
        ----------
        :param h: The new handler.
        :type h: BaseFailureHandler

        Raises
        ------
        :raises TypeError: If h is not an instance of BaseFailureHandler.
        """

        # type checks
        check_subclass(BaseFailureHandler, h)

        self.__handler = h

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


def fallback(fallback_func, *args, **kwargs):
    """
    fallback
    ========
    If the decorated function fails, the fallback function will be executed.

    Parameters
    ----------
    :param fallback_func: The fallback function.
    :type fallback_func: Callable[..., Any]
    :param args: The args to pass to the fallback function.
    :type args: Any
    :param kwargs: The kwargs to pass to the fallback function.
    :type kwargs: Any

    Raises
    ------
    :raise TypeError: If func is not callable.

    Example Usage
    -------------
    ```python
    >>> def failure_handler():
    ...     print("An error occurred. Suppressing...")
    ...
    >>> @fallback(failure_handler)
    ... def risky():
    ...     raise TypeError
    ...
    >>> risky()
    An error occurred. Suppressing...
    ```
    """

    # type checks
    check_callable(fallback_func)

    def decorator(func):
        @wraps(func)
        def wrapper(*w_args, **w_kwargs):
            try:
                return func(*w_args, **w_kwargs)
            except Exception:
                return fallback_func(*args, **kwargs)

        return wrapper

    return decorator
