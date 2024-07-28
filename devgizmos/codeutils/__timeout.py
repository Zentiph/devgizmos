"""
codeutils.__timeout
===================
Module containing the Timeout class and related functionality.
"""

from functools import wraps
from inspect import currentframe
from platform import system

from ..errguards import ensure_in_bounds, ensure_instance_of, ensure_superclass_of

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
        ensure_instance_of(cutoff, (int, float))
        ensure_superclass_of(BaseException, exc)

        # value checks
        ensure_in_bounds(cutoff, 0, None, inclusive=False)

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
        ensure_superclass_of(BaseException, e)

        self.__exc = e
