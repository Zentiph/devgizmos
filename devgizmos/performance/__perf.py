"""
performance.__perf
==================
Module containing performance related functionality.
"""

from functools import wraps
from statistics import mean
from time import perf_counter_ns

from .._internal import TIME_UNITS
from ..checks import check_in_bounds, check_type, check_value


class TimerNotStartedError(Exception):
    """Exception to raise if a Timer method is called when the Timer has not been started."""


class TimerReactivationError(Exception):
    """Exception to raise if 'Timer.start()' is called when the Timer has already started."""


# pylint: disable=too-many-instance-attributes
class Timer:
    """Class for timing code."""

    def __init__(self, unit="ns", precision=3):
        """
        Timer
        =====
        Class that times how long code takes to run.
        Can be used as a standard class, a context manager, or a decorator.

        Parameters
        ----------
        :param unit: The unit of time to use, defaults to "ns".
        - Supported units are "ns", "us", "ms", "s".\n
        :type unit: Literal["ns", "us", "ms", "s"], optional
        :param precision: The precision to use when rounding the time, defaults to 3
        :type precision: int, optional

        Raises
        ------
        :raises TypeError: If precision is not an int.
        :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.

        Example Usage (Standard)
        ------------------------
        ```python
        >>> # create the timer
        >>> tmr = Timer("ms")
        >>> # start the timer
        >>> tmr.start()
        >>> for _ in range(100_000):
        ...     pass
        ...
        >>> # pause the timer
        >>> tmr.pause()
        >>> # this for loop won't be timed
        >>> for _ in range(100_000):
        ...     pass
        ...
        >>> # resume the timer
        >>> tmr.resume()
        >>> # stop the timer
        >>> tmr.stop()
        >>> # get the elapsed time
        >>> tmr.elapsed
        4.676
        >>> # reset the timer
        >>> tmr.reset()
        >>> tmr.elapsed
        0.0
        ```
        Example Usage (Context Manager)
        -------------------------------
        ```python
        >>> with Timer("ms") as t:
        ...     for _ in range(100_000):
        ...             pass
        ...     t.pause()
        ...     for _ in range(100_000):
        ...             pass
        ...     t.resume()
        ...
        >>> t.elapsed
        3.306
        ```
        Example Usage (Decorator)
        -------------------------
        ```python
        >>> tmr = Timer("ms")
        >>>
        >>> @tmr
        ... def perf_test():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> perf_test()
        >>> tmr.elapsed
        1.837
        ```
        """

        # type checks
        check_type(precision, int)

        unit = unit.lower()
        # value checks
        check_value(unit, TIME_UNITS)

        self.__unit = unit
        self.__precision = precision

        self.__initial_time = 0.0  # placeholder
        self.__last_unpaused = 0.0  # placeholder
        self.__elapsed_time = 0.0

        self.__started = False
        self.__paused = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type_, value, traceback):
        self.stop()

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
            return result

        return wrapper

    @property
    def elapsed(self):
        """
        Timer.elapsed
        =============
        Returns the time elapsed so far.
        """

        if not self.__paused:
            now = perf_counter_ns()
            self.__elapsed_time += now - self.__last_unpaused
            self.__last_unpaused = now

        converted = self.__elapsed_time / (1000 ** TIME_UNITS.index(self.__unit))
        rounded = round(converted, self.__precision)

        return rounded

    def start(self):
        """
        Timer.start()
        =============
        Starts the timer.
        """

        if self.__started:
            raise TimerReactivationError(
                "'Timer.start()' was called when Timer was already activated."
            )

        self.__initial_time = perf_counter_ns()
        self.__last_unpaused = self.__initial_time

        self.__started = True

    def stop(self):
        """
        Timer.stop()
        ============
        Stops the timer.
        """

        if not self.__started:
            raise TimerNotStartedError(
                "Timer must be started to use 'Timer.stop()'. To start the Timer, use 'Timer.start()'."
            )

        self.pause()
        self.__started = False

    def pause(self):
        """
        Timer.pause()
        =============
        Pauses the timer.
        """

        if not self.__started:
            raise TimerNotStartedError(
                "Timer must be started to use 'Timer.pause()'. To start the Timer, use 'Timer.start()'."
            )

        if not self.__paused:
            self.__elapsed_time += perf_counter_ns() - self.__last_unpaused
            self.__paused = True

    def resume(self):
        """
        Timer.resume()
        ==============
        Resumes the timer.
        """

        if not self.__started:
            raise TimerNotStartedError(
                "Timer must be started to use 'Timer.resume()'. To start the Timer, use 'Timer.start()'."
            )

        self.__last_unpaused = perf_counter_ns()
        self.__paused = False

    def reset(self):
        """
        Timer.reset()
        =============
        Resets the timer's time settings to their initial state.
        """

        self.__elapsed_time = 0.0
        self.__initial_time = 0.0
        self.__last_unpaused = 0.0


class Benchmark:
    """Class for benchmarking code."""

    def __init__(self, trials=10, unit="ns", precision=3):
        """
        Benchmark
        =========
        Class to be used as a decorator that runs code multiple times
        and reports the average, minimum, and maximum execution times.

        Parameters
        ----------
        :param trials: The number of times to run the code, defaults to 10.
        :type trials: int
        :param unit: The unit of time to use, defaults to "ns".
        - Supported units are "ns", "us", "ms", "s".\n
        :type unit: Literal["ns", "us", "ms", "s"], optional
        :param precision: The precision to use when rounding the time, defaults to 3
        :type precision: int, optional

        Raises
        ------
        :raises TypeError: If trials is not an int.
        :raises TypeError: If precision is not an int.
        :raises ValueError: If trials is less than 1.
        :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.

        Example Usage
        -------------
        ```python
        >>> benchmark = Benchmark(unit="ms")
        >>>
        >>> @benchmark
        ... def perf_test():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> perf_test()
        >>>
        >>> benchmark.average
        1.671
        >>> benchmark.minimum
        1.522
        >>> benchmark.maximum
        1.813
        ```
        """

        # type checks
        check_type(trials, int)
        check_type(precision, int)

        unit = unit.lower()
        # value checks
        check_in_bounds(trials, 1, None)
        check_value(unit, TIME_UNITS)

        self.__trials = trials
        self.__unit = unit
        self.__precision = precision

        self.__avg = 0.0  # placeholder
        self.__min = 0.0  # placeholder
        self.__max = 0.0  # placeholder

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            returned = None

            for i in range(self.__trials):
                start_time = perf_counter_ns()

                if i == len(range(self.__trials)) - 1:
                    returned = func(*args, **kwargs)
                else:
                    func(*args, **kwargs)

                delta = perf_counter_ns() - start_time
                elapsed = delta / (1000 ** TIME_UNITS.index(self.__unit))

                results.append(elapsed)

            self.__avg = float(round(mean(results), self.__precision))
            self.__min = float(round(min(results), self.__precision))
            self.__max = float(round(max(results), self.__precision))

            return returned

        return wrapper

    @property
    def average(self):
        """
        Benchmark.average
        =================
        Returns the average time it took the code to execute.
        """

        return self.__avg

    @property
    def minimum(self):
        """
        Benchmark.minimum
        =================
        Returns the minimum time it took the code to execute.
        """

        return self.__min

    @property
    def maximum(self):
        """
        Benchmark.maximum
        =================
        Returns the maximum time it took the code to execute.
        """

        return self.__max
