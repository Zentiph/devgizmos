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


class NotStartedError(Exception):
    """Exception to raise if one of a class's methods is called before its start() method has been called."""


class ReactivationError(Exception):
    """
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
        >>> # pause it
        >>> mp.pause()
        >>> # get the memory used
        >>> mp.memory_used
        9.544
        >>> # resume it
        >>> mp.resume()
        >>> for _ in range(100_000):
        ...     pass
        ...
        >>> # end the profiling
        >>> mp.stop()
        >>> mp.memory_used
        8.919
        ```

        Example Usage (Context Manager)
        -------------------------------
        ```python
        >>> with MemoryProfiler() as mp:
        ...     for _ in range(100_000):
        ...             pass
        ...     mp.memory_used
        ...     for _ in range(100_000):
        ...             pass
        ...
        0.608
        >>> mp.memory_used
        1.168
        ```

        Example Usage (Decorator)
        -------------------------
        ```python
        >>> mp = MemoryProfiler()
        >>>
        >>> @mp
        ... def perf_example():
        ...     for _ in range(100_000):
        ...             pass
        ...
        >>> perf_example()
        >>>
        >>> mp.memory_used
        0.528
        ```
        """

        # type checks
        check_type(precision, int)

        unit = unit.lower()
        # value checks
        check_value(unit, DEC_MEM_UNITS + BIN_MEM_UNITS)

        self.__unit = unit
        self.__precision = precision

        if self.__unit in DEC_MEM_UNITS:
            self.__unit_type = "dec"
        else:
            self.__unit_type = "bin"

        self.__start_mem = 0
        self.__end_mem = 0

        self.__paused = False
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

    def pause(self):
        """
        MemoryProfiler.pause()
        ======================
        Pauses memory profiling.
        """

        if not self.__running:
            raise NotStartedError(
                "MemoryProfiler must be started to use 'MemoryProfiler.pause()'."
                + "To start the MemoryProfiler, use 'MemoryProfiler.start()'."
            )

        if not self.__paused:
            self.__end_mem = take_snapshot()
            tm_stop()
            self.__paused = True

    def resume(self):
        """
        MemoryProfiler.resume()
        =======================
        Resumes memory profiling.
        """

        if not self.__running:
            raise NotStartedError(
                "MemoryProfiler must be started to use 'MemoryProfiler.resume()'."
                + "To start the MemoryProfiler, use 'MemoryProfiler.start()'."
            )

        if self.__paused:
            tm_start()
        self.__paused = False

    @property
    def memory_used(self):
        """
        MemoryProfiler.memory_used
        ==========================
        Returns the memory usage of the profiled code.
        """

        if self.__running and not self.__paused:
            self.__end_mem = take_snapshot()

        comparison = self.__end_mem.compare_to(self.__start_mem, "lineno")
        mem_used = sum(stat.size for stat in comparison)
        if self.__unit_type == "dec":
            converted = mem_used / (1000 ** DEC_MEM_UNITS.index(self.__unit))
        else:
            converted = mem_used / (1024 ** BIN_MEM_UNITS.index(self.__unit))
        rounded = round(converted, self.__precision)

        return rounded
