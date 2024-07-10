"""
contmngrs
=========
Module containing context managers.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:\n
contextlib
- contextmanager\n
logging
- INFO
- Logger\n
os
- chdir
- environ
- getcwd
- remove
- rmdir\n
random
- getstate
- seed
- setstate\n
tempfile
- NamedTemporaryFile
- mkdtemp\n
time
- perf_counter_ns
- sleep
"""

from .__contmngrs import (
    change_dir,
    change_env,
    retry_on,
    seed,
    suppress,
    tempdir,
    tempfile,
    timer,
)
