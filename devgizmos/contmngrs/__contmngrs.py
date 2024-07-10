"""
contmngrs.__contmngrs
=====================
Module containing context managers.
"""

from contextlib import contextmanager
from logging import INFO, Logger
from os import chdir, environ, getcwd, remove, rmdir
from random import getstate
from random import seed as rand_seed
from random import setstate
from tempfile import NamedTemporaryFile, mkdtemp
from time import perf_counter_ns

from .._internal import LOGGING_LEVELS, TIME_UNITS, handle_result_reporting
from ..checks import check_type, check_value


@contextmanager
def seed(a, version=2):
    """
    seed
    ====
    Context manager that initializes the code within with the given seed.
    Can also be used as a decorator.

    Parameters
    ----------
    :param a: The seed.
    :type a: int | float | str | bytes | bytearray | None
    :param version: The version to use.
    :type version: Literal[1, 2]

    Example Usage
    -------------
    ```python
    >>> from random import random
    >>>
    >>> with seed(18):
    ...     print(random())
    ...
    0.18126486333322134
    >>> with seed(18):
    ...     print(random())
    ...
    0.18126486333322134
    >>>
    >>> @seed(18)
    ... def pt_rnd():
    ...     print(random())
    ...
    >>> pt_rnd()
    0.18126486333322134
    >>> pt_rnd()
    0.18126486333322134
    ```
    """

    orig_state = getstate()
    rand_seed(a, version)

    try:
        yield
    finally:
        setstate(orig_state)


@contextmanager
def timer(unit="ns", precision=3, *, fmt="", logger=None, level=INFO):
    """
    timer
    =====
    Context manager that times how long the code within takes to run.
    Can also be used as a decorator.

    Parameters
    ----------
    :param unit: The unit of time to use, defaults to "ns".
    - Supported units are "ns", "us", "ms", "s".\n
    :type unit: Literal["ns", "us", "ms", "s"], optional
    :param precision: The precision to use when rounding the time, defaults to 3
    :type precision: int, optional
    :param fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message.
    - Enter an unformatted string with the following fields to include their values
    - elapsed: The time elapsed by the code's execution.
    - unit: The unit used in the timing.
    - Ex: fmt="Code took {elapsed} {unit} to run."\n
    :type fmt: str, optional
    :param logger: The logger to use if desired, defaults to None.
    - If a logger is used, the result message will not be printed and will instead be passed to the logger.\n
    :type logger: Logger | None, optional
    :param level: The logging level to use, defaults to logging.INFO (20).
    :type level: LoggingLevel, optional

    Raises
    ------
    :raises TypeError: If precision is not an int.
    :raises TypeError: If fmt is not a str.
    :raises TypeError: If logger is not a logging.Logger.
    :raises ValueError: If unit is not 'ns', 'us', 'ms', or 's'.
    :raises ValueError: If level is not a level from logging.

    Example Usage
    -------------
    ```python
    >>> from time import sleep
    >>>
    >>> with timer(unit="s"):
    ...     sleep(2)
    ...
    [TIMER]: CODE BLOCK RAN IN 2.0 s
    >>>
    >>> @timer(unit="s")
    ... def perf_example():
    ...     sleep(2)
    ...
    >>> perf_example()
    [TIMER]: CODE BLOCK RAN IN 2.0 s
    ```
    """

    # type checks
    check_type(precision, int)
    check_type(fmt, str)
    check_type(logger, Logger, optional=True)

    # value checks
    check_value(unit, TIME_UNITS)
    check_value(level, LOGGING_LEVELS)

    local_unit = unit.lower()

    start_time = perf_counter_ns()

    try:
        yield

    finally:
        delta = perf_counter_ns() - start_time
        elapsed = delta / (1000 ** TIME_UNITS.index(local_unit))
        rounded = round(elapsed, precision)

        fmt_kwargs = {
            "elapsed": rounded,
            "unit": local_unit,
        }
        default = f"[TIMER]: CODE BLOCK RAN IN {rounded} {local_unit}"

        handle_result_reporting(fmt, default, logger, level, **fmt_kwargs)


@contextmanager
def tempdir():
    """
    tempdir
    =======
    Context manager that creates a temporary directory, deleting it on exit.

    Example Usage
    -------------
    ```python
    >>> with tempdir() as td:
    ...     print(td)
    ...
    'C:\\Users\\user\\AppData\\Local\\Temp\\tmpcnssgvv3'
    >>> # may vary depending on OS or machine setup
    ```
    """

    td = mkdtemp()
    try:
        yield td
    finally:
        rmdir(td)


@contextmanager
def tempfile():
    """
    tempfile
    ========
    Context manager that creates a temporary file, deleting it upon exit.

    Example Usage
    -------------
    ```python
    >>> with tempfile() as tf:
    ...     print(tf)
    ...
    'C:\\Users\\user\\AppData\\Local\\Temp\\tmp_fmy_5nk'
    ```
    """

    tf = NamedTemporaryFile(delete=False)
    try:
        yield tf.name
    finally:
        tf.close()
        remove(tf.name)


@contextmanager
def change_dir(path):
    """
    change_dir
    ==========
    Context manager that temporarily changes the current working directory.

    Parameters
    ----------
    :param path: The new working directory path.
    :type path: str

    Raises
    ------
    :raises TypeError: If path is not a str.

    Example Usage
    -------------
    ```python
    >>> from os import getcwd
    >>>
    >>> with change_dir("C:/Users/users/Desktop"):
    ...     print(getcwd())
    ...
    'C:\\Users\\users\\Desktop'
    >>>
    >>> getcwd()
    'C:\\Users\\users\\Desktop\\Programming\\Python\\devgizmos'
    ```
    """

    orig_dir = getcwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(orig_dir)


@contextmanager
def set_env(**env_vars):
    """
    set_env
    =======
    Context manager that temporarily sets environment variables.

    Parameters
    ----------
    :param env_vars: The environment variables to set.
    :type env_vars: str

    Raises
    ------
    :raises TypeError: If any env var in env_vars is not a str.

    Example Usage
    -------------
    ```python
    >>> from os import environ
    >>>
    >>> with set_env(PATH="/tmp"):
    ...     print(environ["PATH"])
    ...
    /tmp
    >>>
    >>> print(environ["PATH"])
    'C:\\Previous\\Path1;C:\\Previous\\Path2'
    >>> # etc
    ```
    """

    for var in env_vars.values():
        check_type(var, str)

    orig_env = environ.copy()
    environ.update(env_vars)

    try:
        yield
    finally:
        environ.clear()
        environ.update(orig_env)


@contextmanager
def suppress(*exceptions):
    """
    suppress
    ========
    Context manager that suppresses specified exceptions depending on the user.

    Parameters
    ----------
    :param exceptions: The exceptions provided to be suppress.
    :type exceptions: Exception

    Example Usage
    -------------
    ```python
    >>> with suppressor(FileNotFoundError):
    ...     open("example_file.txt")
    ...
    (No traceback, exception suppressed)
    ```
    """

    try:
        yield
    except exceptions:
        pass
