"""decorators
-------------
Module containing useful decorators.

This module utilizes the following functionality from built-in modules/packages:

functools
    - lru_cache
    - wraps

logging
    - ERROR
    - INFO
    - WARNING
    - Logger

platform
    - system

re
    - findall

signal (Unix)
    - SIGALRM
    - alarm
    - signal

threading (Windows)
    - Thread

time
    - perf_counter_ns
    - sleep

typing
    - Any
    - Callable
    - TypeVar
    - get_type_hints

warnings
    - warn
"""

from .__decorators import *
