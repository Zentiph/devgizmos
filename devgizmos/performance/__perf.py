"""
performance.__perf
==================
Module containing performance related functionality.
"""

from functools import wraps
from statistics import mean
from time import perf_counter_ns
from tracemalloc import start as tm_start
from tracemalloc import stop as tm_stop
from tracemalloc import take_snapshot

from ..checks import check_in_bounds, check_type, check_value

TIME_UNITS = ("ns", "us", "ms", "s")
DEC_MEM_UNITS = ("b", "kb", "mb", "gb")
BIN_MEM_UNITS = ("b", "kib", "mib", "gib")
MEM_UNITS = BIN_MEM_UNITS + DEC_MEM_UNITS


class NotStartedError(Exception):
    """
    NotStartedError
    ===============
    Exception to raise if one of a class's methods is called before its start() method has been called.
    """


class ReactivationError(Exception):
    """
    ReactivationError
    =================
    Exception to raise if a class's start() is called when
    its start() method has been previously called and before its stop() method has been called.
    """


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
        :raises ReactivationError: If the start() method is called twice before the stop() method has been called.
        :raises NotStartedError: If any methods other than start() are called before start().

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
        >>> # enter the context manager
        >>> with Timer("ms") as t:
        ...     for _ in range(100_000):
        ...             pass
        ...     # pause the timer to ignore this for loop
        ...     t.pause()
        ...     for _ in range(100_000):
        ...             pass
        ...     # resume it
        ...     t.resume()
        ...
        >>> # get the time elapsed
        >>> t.elapsed
        1.947
        ```

        Example Usage (Decorator)
        -------------------------
        ```python
        >>> # create the timer object
        >>> tmr = Timer("ms")
        >>>
        >>> # decorate a function with it
        >>> @tmr
        ... def perf_test():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> # call the function
        >>> perf_test()
        >>>
        >>> # get the time elapsed
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

        Return
        ------
        :return: The time elapsed.
        :rtype: int | float
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
        Starts the timer. Overrides old data.
        """

        if self.__started:
            raise ReactivationError(
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
            raise NotStartedError(
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
            raise NotStartedError(
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
            raise NotStartedError(
                "Timer must be started to use 'Timer.resume()'. To start the Timer, use 'Timer.start()'."
            )

        if self.__paused:
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

    @property
    def unit(self):
        """
        Timer.unit
        ==========
        Returns the unit being used by the Timer.

        Return
        ------
        :return: The unit being used by the Timer.
        :rtype: Literal["ns", "us", "ms", "s"]
        """

        return self.__unit

    @unit.setter
    def unit(self, u, /):
        """
        Timer.unit()
        ============
        Sets the unit for the Timer.

        Parameters
        ----------
        :param u: The new unit.
        :type u: Literal["ns", "us", "ms", "s"]

        Raises
        ------
        :raises ValueError: If u is not "ns", "us", "ms", or "s".
        """

        # value checks
        check_value(u, TIME_UNITS)

        self.__unit = u

    @property
    def precision(self):
        """
        Timer.precision
        ===============
        Returns the precision being used by the Timer.

        Return
        ------
        :return: The precision being used by the Timer.
        :rtype: int
        """

        return self.__precision

    @precision.setter
    def precision(self, p, /):
        """
        Timer.precision()
        =================
        Sets the precision for the Timer.

        Parameters
        ----------
        :param p: The new precision.
        :type p: int

        Raises
        ------
        :raises ValueError: If p is not an int.
        """

        # type checks
        check_value(p, int)

        self.__precision = p


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
        >>> # create the benchmark
        >>> benchmark = Benchmark(unit="ms")
        >>>
        >>> # decorate it to a function
        >>> @benchmark
        ... def perf_test():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> perf_test()
        >>> # get the function's benchmark stats
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

        Return
        ------
        :return: The average time.
        :rtype: float
        """

        return self.__avg

    @property
    def minimum(self):
        """
        Benchmark.minimum
        =================
        Returns the minimum time it took the code to execute.

        Return
        ------
        :return: The minimum time.
        :rtype: float
        """

        return self.__min

    @property
    def maximum(self):
        """
        Benchmark.maximum
        =================
        Returns the maximum time it took the code to execute.

        Return
        ------
        :return: The maximum time.
        :rtype: float
        """

        return self.__max

    @property
    def trials(self):
        """
        Benchmark.trials
        ================
        Returns the number of trials the Benchmark will run.

        Return
        ------
        :return: The number of trials to be run.
        :rtype: int
        """

        return self.__trials

    @trials.setter
    def trials(self, t, /):
        """
        Benchmark.trials()
        ==================
        Sets the number of trials the Benchmark will run.

        Parameters
        ----------
        :param t: The new number of trials to run.
        :type t: int

        Raises
        ------
        :raises TypeError: If t is not an int.
        :raises ValueError: If t is less than or equal to 0.
        """

        # type checks
        check_type(t, int)

        # value checks
        check_in_bounds(t, 1, None)

        self.__trials = t

    @property
    def unit(self):
        """
        Benchmark.unit
        ==============
        Returns the unit being used by the Benchmark.

        Return
        ------
        :return: The unit being used by the Benchmark.
        :rtype: Literal["ns", "us", "ms", "s"]
        """

        return self.__unit

    @unit.setter
    def unit(self, u, /):
        """
        Benchmark.unit()
        ================
        Sets the unit for the Benchmark.

        Parameters
        ----------
        :param u: The new unit.
        :type u: Literal["ns", "us", "ms", "s"]

        Raises
        ------
        :raises ValueError: If u is not "ns", "us", "ms", or "s".
        """

        # value checks
        check_value(u, TIME_UNITS)

        self.__unit = u

    @property
    def precision(self):
        """
        Benchmark.precision
        ===================
        Returns the precision being used by the Benchmark.

        Return
        ------
        :return: The precision being used by the Benchmark.
        :rtype: int
        """

        return self.__precision

    @precision.setter
    def precision(self, p, /):
        """
        Benchmark.precision()
        =====================
        Sets the precision for the Benchmark.

        Parameters
        ----------
        :param p: The new precision.
        :type p: int

        Raises
        ------
        :raises ValueError: If p is not an int.
        """

        # type checks
        check_value(p, int)

        self.__precision = p


class MemoryProfiler:
    """Class for profiling memory usage."""

    def __init__(self, unit="kb", precision=3):
        """
        MemoryProfiler
        ==============
        Class for profiling memory usage.
        Can be used as a standard class, a context manager, or a decorator.

        Parameters
        ----------
        :param unit: The unit of memory to use, defaults to "kb".
        - Supported decimal units are "b", "kb", "mb", "gb".
        - Supported binary units are "b", "kib", "mib", "gib".\n
        :type unit: Literal["b", "kb", "mb", "gb", "kib", "mib", "gib"]
        :param precision: The precision to use when rounding the memory, defaults to 3
        :type precision: int, optional

        Raises
        ------
        :raises TypeError: If precision is not an int.
        :raises ValueError: If unit is not 'b', 'kb', 'mb', 'gb', 'kib', 'mib', or 'gib'.
        :raises ReactivationError: If the start() method is called twice before the stop() method has been called.
        :raises NotStartedError: If any methods other than start() are called before start().

        Example Usage (Standard)
        ------------------------
        ```python
        >>> # create the memory profiler
        >>> mp = MemoryProfiler()
        >>> # start it
        >>> mp.start()
        >>> for _ in range(100_000):
        ...     pass
        ...
        >>> # stop it
        >>> mp.stop()
        >>> # get the memory used
        >>> mp.memory_used
        9.544
        ```

        Example Usage (Context Manager)
        -------------------------------
        ```python
        >>> # enter the context manager block
        >>> with MemoryProfiler() as mp:
        ...     for _ in range(100_000):
        ...             pass
        ...     # get the memory used up to this point
        ...     # (will partially skew data due to getting memory also taking memory)
        ...     # (this is generally negligible unless working with small quantities of data)
        ...     mp.memory_used
        ...     for _ in range(100_000):
        ...             pass
        ...
        0.608
        >>> # get the memory used after
        >>> mp.memory_used
        1.168
        ```

        Example Usage (Decorator)
        -------------------------
        ```python
        >>> # create the memory profiler
        >>> mp = MemoryProfiler()
        >>>
        >>> # decorate a function with it
        >>> @mp
        ... def perf_example():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> # run the function
        >>> perf_example()
        >>>
        >>> # get the memory used
        >>> mp.memory_used
        0.528
        ```
        """

        # type checks
        check_type(precision, int)

        unit = unit.lower()
        # value checks
        check_value(unit, MEM_UNITS)

        self.__unit = unit
        self.__precision = precision

        if self.__unit in DEC_MEM_UNITS:
            self.__unit_type = "dec"
        else:
            self.__unit_type = "bin"

        self.__start_mem = None  # placeholder
        self.__end_mem = None  # placeholder

        self.__running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type_, value, traceback):
        self.stop()

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.start()
            result = func(*args, **kwargs)
            self.stop()

            return result

        return wrapper

    def start(self):
        """
        MemoryProfiler.start()
        ======================
        Starts listening for memory usage. Overrides old data.
        """

        if self.__running:
            raise ReactivationError(
                "'MemoryProfiler.start()' was called while MemoryProfiler was already activated."
            )

        tm_start()
        self.__start_mem = take_snapshot()
        self.__running = True

    def stop(self):
        """
        MemoryProfiler.stop()
        =====================
        Stops listening for memory usage.
        """

        if not self.__running:
            raise NotStartedError(
                "MemoryProfiler must be started to use 'MemoryProfiler.stop()'."
                + "To start the MemoryProfiler, use 'MemoryProfiler.start()'."
            )

        self.__end_mem = take_snapshot()
        tm_stop()
        self.__running = False

    @property
    def memory_used(self):
        """
        MemoryProfiler.memory_used
        ==========================
        Returns the memory usage of the profiled code.

        Return
        ------
        :return: The memory used, rounded using the MemoryProfiler's unit.
        :rtype: int | float
        """

        if self.__running:
            self.__end_mem = take_snapshot()

        comparison = self.__end_mem.compare_to(self.__start_mem, "lineno")
        mem_used = sum(stat.size for stat in comparison)
        if self.__unit_type == "dec":
            converted = mem_used / (1000 ** DEC_MEM_UNITS.index(self.__unit))
        else:
            converted = mem_used / (1024 ** BIN_MEM_UNITS.index(self.__unit))
        rounded = round(converted, self.__precision)

        return rounded

    @property
    def unit(self):
        """
        MemoryProfiler.unit
        ===================
        Returns the unit being used by the MemoryProfiler.

        Return
        ------
        :return: The unit being used by the MemoryProfiler.
        :rtype: Literal["b", "kb", "mb", "gb", "kib", "mib", "gib"]
        """

        return self.__unit

    @unit.setter
    def unit(self, u, /):
        """
        MemoryProfiler.unit()
        =====================
        Sets the unit for the MemoryProfiler.

        Parameters
        ----------
        :param u: The new unit.
        :type u: Literal["b", "kb", "mb", "gb", "kib", "mib", "gib"]

        Raises
        ------
        :raises ValueError: If u is not "b", "kb", "mb", "gb", "kib", "mib", or "gib".
        """

        # value checks
        check_value(u, MEM_UNITS)

        self.__unit = u

    @property
    def precision(self):
        """
        MemoryProfiler.precision
        ========================
        Returns the precision being used by the MemoryProfiler.

        Return
        ------
        :return: The precision being used by the MemoryProfiler.
        :rtype: int
        """

        return self.__precision

    @precision.setter
    def precision(self, p, /):
        """
        MemoryProfiler.precision()
        ==========================
        Sets the precision for the MemoryProfiler.

        Parameters
        ----------
        :param p: The new precision.
        :type p: int

        Raises
        ------
        :raises ValueError: If p is not an int.
        """

        # type checks
        check_value(p, int)

        self.__precision = p
