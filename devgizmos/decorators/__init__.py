"""
decorators
==========
Module containing decorators such as timer, retry, benchmark, etc.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:
asyncio
- sleep\n
collections
- OrderedDict
functools
- wraps\n
logging
- ERROR
- INFO
- WARNING
- Logger\n
platform
- system\n
re
- findall\n
signal (Unix)
- SIGALRM
- alarm
- signal\n
statistics
- mean\n
threading (Windows)
- Thread\n
time
- perf_counter
- perf_counter_ns
- sleep\n
typing
- Any
- Callable
- TypeVar
- Union
- get_type_hints\n
warnings
- warn
"""

from .__decorators import (
    ConditionError,
    UnsupportedOSError,
    async_retry,
    benchmark,
    benchmark_rs,
    cache,
    conditional,
    decorate_all_methods,
    deprecated,
    error_logger,
    fallback,
    immutable,
    lazy_property,
    rate_limit,
    retry,
    singleton,
    suppressor,
    timeout,
    timer,
    timer_rs,
    tracer,
    type_checker,
)
