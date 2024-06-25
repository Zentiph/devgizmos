"""
decorators
==========


Description
-----------

Module containing decorators such as timer, retry, benchmark, etc.


Built-in Utilizations
---------------------

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

from .__decorators import (
    ConditionError,
    UnsupportedOSError,
    benchmark,
    cache,
    call_logger,
    conditional,
    decorate_all_methods,
    deprecated,
    error_logger,
    rate_limit,
    retry,
    singleton,
    suppress,
    timeout,
    timer,
    tracer,
    type_checker,
)
