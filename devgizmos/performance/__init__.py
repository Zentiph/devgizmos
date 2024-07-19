"""
performance
===========
Module containing performance related functionality such as timing/benchmark utility.

Built-in Utilizations
---------------------
functools
- wraps\n
statistics
- mean\n
time
- perf_counter_ns\n
tracemalloc
- start
- stop
- take_snapshot\n
"""

from .__perf import Benchmark, MemoryProfiler, NotStartedError, ReactivationError, Timer
