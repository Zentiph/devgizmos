"""decorators
-------------
Module containing useful decorators.

This module utilizes the following functionality from built-in modules/packages:

functools
    - wraps

platform
    - system

signal (Linux & MacOS)
    - alarm
    - signal
    - SIGALRM

threading (Windows)
    - Thread

time
    - perf_counter_ns
    - sleep
"""

from .__decorators import *
