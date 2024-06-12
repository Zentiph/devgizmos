"""decorators
-------------
Module containing useful decorators.

This module utilizes the following functionality from built-in modules/packages:

functools
    - wraps

logging
    - getLogger

platform
    - system

signal (Unix)
    - alarm
    - signal
    - SIGALRM

threading (Windows)
    - Thread

time
    - perf_counter_ns
    - sleep

typing
    - get_type_hints

warnings
    - warn
"""

from .__decorators import *
