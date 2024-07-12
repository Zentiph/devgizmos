"""
contmngrs
=========
Module containing context managers.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:\n
contextlib
- contextmanager\n
cProfile\n
io
- StringIO\n
logging
- INFO
- Logger\n
os
- chdir
- environ
- getcwd
- remove
- rmdir\n
pstats\n
random
- getstate
- seed
- setstate\n
tempfile
- NamedTemporaryFile
- mkdtemp\n
time
- perf_counter_ns
- sleep\n
threading
- Lock
"""

from .__contmngrs import (
    change_dir,
    change_env,
    lock_handler,
    profile,
    retry_on,
    seed,
    suppress,
    tempdir,
    tempfile,
    timer,
)
