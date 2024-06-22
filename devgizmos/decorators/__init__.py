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

statistics
- mean

threading (Windows)
- Thread

time
- perf_counter
- perf_counter_ns
- sleep

typing
- Any
- Callable
- TypeVar
- Union
- get_type_hints

warnings
- warn
"""

from .__decorators import *
