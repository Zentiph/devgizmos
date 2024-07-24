"""
codeutils.__retry
=================
Module containing the Retry class.
"""

from asyncio import sleep as async_sleep
from functools import wraps
from time import sleep

from ..checks import check_callable, check_in_bounds, check_subclass, check_type


class Retry:
    """Class for retrying failed code."""

    def __init__(
        self,
        max_attempts,
        delay,
        backoff_strategy=None,
        exceptions=(Exception,),
        raise_last=True,
        asynchronous=False,
    ):
        """
        Retry
        =====
        Class used as a decorator that retries a function if it fails
        up until the maximum number of attempts is reached.

        Parameters
        ----------
        :param max_attempts: The maximum number of times to attempt running
        the decorated function, including the first time.
        :type max_attempts: int
        :param delay: The time in seconds to wait after each retry.
        :type delay: int
        :param backoff_strategy: A function to determine the delay after each attempt, or None for no strategy.
        - Ex: def backoff_strategy(delay: int | float, attempt: int) -> int | float
        - The function should take delay as the first argument, and the attempt number as the second argument.
        - The function should return an int or float for the new delay time.
        - The delay will be updated BEFORE sleeping during each attempt loop.\n
        :type backoff_strategy: Callable[[int | float, int], int | float]
        :param exceptions: A tuple of the exceptions to catch and retry on, defaults to (Exception,)
        :type exceptions: Tuple[Type[BaseException], ...], optional
        :param raise_last: Whether to raise the final exception raised when all attempts fail,
        defaults to True
        :type raise_last: bool, optional
        :param asynchronous: Whether to apply the retries asynchronously (for async functions), defaults to False.
        :type asynchronous: bool, optional

        Raises
        ------
        :raises TypeError: If max_attempts is not an int.
        :raises TypeError: If delay is not an int or float.
        :raises TypeError: If backoff_strategy is not callable or None.
        :raises TypeError: If backoff_strategy does not return an int or float.
        :raises TypeError: If exceptions is not a tuple.
        :raises TypeError: If an item inside exceptions is not an instance of BaseException.
        :raises TypeError: If raise_last is not a bool.
        :raises TypeError: If asynchronous is not a bool.
        :raises ValueError: If max_attempts is less than 1.
        :raises ValueError: If delay is less than 0.

        Example Usage
        -------------
        ```python
        >>> from random import random
        >>>
        >>> # for one time use, initialize the class while using it as a decorator
        >>> @Retry(3, 1)
        ... def risky():
        ...     if random() > 0.5:
        ...         raise TypeError
        ...
        >>> risky()
        >>>
        >>> # to reuse, edit, and get info from the class, give it its own variable
        >>> retry = cutils.Retry(3, 1)
        >>>
        >>> @retry
        ... def risky():
        ...     if random() > 0.5:
        ...         raise TypeError
        ...
        >>> risky()
        >>> # get the errors caught
        >>> retry.caught
        [TypeError()]
        >>> # clear the error list for future use
        >>> retry.clear_caught()
        >>>
        ```
        """

        # type checks
        check_type(max_attempts, int)
        check_type(delay, (int, float))
        if backoff_strategy is not None:
            check_callable(backoff_strategy)
        check_type(exceptions, tuple)
        check_subclass(BaseException, exceptions)
        check_type(raise_last, bool)
        check_type(asynchronous, bool)

        # value checks
        check_in_bounds(max_attempts, 1, None)
        check_in_bounds(delay, 0, None)

        self.__max = max_attempts
        self.__delay = delay
        self.__bs = backoff_strategy
        self.__excs = exceptions
        self.__raise_last = raise_last
        self.__async = asynchronous

        self.__attempts = 0
        self.__caught = []

    def __call__(self, func, /):
        if not self.__async:

            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                delay = self.__delay

                while attempts < self.__max:
                    try:
                        return func(*args, **kwargs)

                    except self.__excs as e:
                        attempts += 1
                        self.__caught.append(e)

                        if attempts >= self.__max and self.__raise_last:
                            raise

                        if self.__bs:
                            delay = self.__bs(delay, attempts)

                        sleep(delay)

                self.__attempts = attempts
                return None

            return wrapper

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempts = 0
            delay = self.__delay

            while attempts < self.__max:
                try:
                    return await func(*args, **kwargs)

                except self.__excs as e:
                    attempts += 1
                    self.__caught.append(e)

                    if attempts >= self.__max and self.__raise_last:
                        raise

                    if self.__bs:
                        delay = self.__bs(delay, attempts)

                    await async_sleep(delay)

            self.__attempts = attempts
            return None

        return async_wrapper

    @property
    def max_attempts(self):
        """
        Retry.max_attempts
        ==================
        Returns the max attempts alloted to Retry object.

        Return
        ------
        :return: The max attempts given to Retry.
        :rtype: int
        """

        return self.__max

    @max_attempts.setter
    def max_attempts(self, m, /):
        """
        Retry.max_attempts()
        ====================
        Sets the max attempts for the Retry object.

        Parameters
        ----------
        :param m: The new max attempts for the Retry.
        :type m: int

        Raises
        ------
        :raises TypeError: If m is not an int.
        :raises ValueError: If m is less than 1.
        """

        # type checks
        check_type(m, int)

        # value checks
        check_in_bounds(m, 1, None)

        self.__max = m

    @property
    def delay(self):
        """
        Retry.delay
        ===========
        Returns the delay of the Retry object.

        Return
        ------
        :return: The delay of the Retry.
        :rtype: int | float
        """

        return self.__delay

    @delay.setter
    def delay(self, d, /):
        """
        Retry.delay()
        =============
        Sets the delay for the Retry object.

        Parameters
        ----------
        :param d: The new delay.
        :type d: int | float

        Raises
        ------
        :raises TypeError: If d is not an int or float.
        :raises ValueError: If d is less than 0.
        """

        # type checks
        check_type(d, (int, float))

        # value checks
        check_in_bounds(d, 0, None)

        self.__delay = d

    @property
    def backoff_strategy(self):
        """
        Retry.backoff_strategy
        ======================
        Returns the backoff strategy of the Retry object.

        Return
        ------
        :return: The backoff strategy.
        :rtype: Callable[[int | float, int], int | float] | None
        """

        return self.__bs

    @backoff_strategy.setter
    def backoff_strategy(self, bs, /):
        """
        Retry.backoff_strategy()
        ========================
        Sets the backoff strategy of the Retry object.

        Parameters
        ----------
        :param bs: The new backoff strategy.
        :type bs: Callable[[int | float, int], int | float] | None

        Raises
        ------
        :raises TypeError: If bs is not callable.
        """

        # type checks
        if bs is not None:
            check_callable(bs)

        self.__bs = bs

    @property
    def exceptions(self):
        """
        Retry.exceptions
        ================
        Returns the exceptions the Retry object will suppress.

        Return
        ------
        :return: The exceptions that will be suppressed.
        :rtype: Tuple[Type[BaseException], ...]
        """

        return self.__excs

    @exceptions.setter
    def exceptions(self, excs, /):
        """
        Retry.exceptions()
        ==================
        Sets the exceptions for the Retry object to suppress.

        Parameters
        ----------
        :param excs: The new exceptions to suppress.
        :type excs: Tuple[Type[BaseException], ...]

        Raises
        ------
        :raises TypeError: If excs is not a tuple of BaseExceptions.
        """

        # type checks
        check_type(excs, tuple)
        check_subclass(BaseException, excs)

        self.__excs = excs

    @property
    def raise_last(self):
        """
        Retry.raise_last
        ================
        Returns whether the Retry object will raise the final exception.

        Return
        ------
        :return: Whether the final exception will be raised.
        :rtype: bool
        """

        return self.__raise_last

    @raise_last.setter
    def raise_last(self, rl, /):
        """
        Retry.raise_last()
        ==================
        Sets whether the Retry object will raise the final exception.

        Parameters
        ----------
        :param rl: Whether to raise the final exception.
        :type rl: bool

        Raises
        ------
        :raises TypeError: If rl is not a bool.
        """

        # type checks
        check_type(rl, bool)

        self.__raise_last = rl

    @property
    def asynchronous(self):
        """
        Retry.asynchronous
        ==================
        Returns whether the Retry object should be executed asynchronously (for async functions).

        Return
        ------
        :return: Whether the Retry object will execute code asynchronously.
        :rtype: bool
        """

        return self.__async

    @asynchronous.setter
    def asynchronous(self, a, /):
        """
        Retry.asynchronous()
        ==================
        Sets whether the Retry object will should run code asynchronously (for async functions).

        Parameters
        ----------
        :param a: Whether to run code asynchronously.
        :type a: bool

        Raises
        ------
        :raises TypeError: If a is not a bool.
        """

        # type checks
        check_type(a, bool)

        self.__async = a

    @property
    def attempts(self):
        """
        Retry.attempts
        ==============
        Returns the attempts used by the most recent Retry call.

        Return
        ------
        :return: The attempts used by the most recent call.
        :rtype: int
        """

        return self.__attempts

    @property
    def caught(self):
        """
        Retry.caught
        ============
        Returns a list of the exceptions caught by the Retry object.

        Return
        ------
        :return: A list of the caught exceptions.
        :rtype: List[Type[BaseException]]
        """

        return self.__caught

    def clear_caught(self):
        """
        Retry.clear_caught()
        ====================
        Clears the list of caught exceptions given when calling Retry.caught.
        """

        self.__caught.clear()
