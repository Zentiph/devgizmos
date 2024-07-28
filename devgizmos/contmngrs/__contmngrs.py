"""
contmngrs.__contmngrs
=====================
Module containing context managers.
"""

from contextlib import contextmanager
import cProfile
from os import chdir, environ, getcwd, remove, rmdir
from random import getstate
from random import seed as rand_seed
from random import setstate
from tempfile import NamedTemporaryFile, mkdtemp
from time import sleep
from concurrent.futures import Future

from ..errguards import (
    ensure_callable,
    ensure_in_bounds,
    ensure_superclass_of,
    ensure_instance_of,
)


@contextmanager
def seed(a, version=2):
    """
    seed
    ----
    Context manager that initializes the code within with the given seed.
    Can also be used as a decorator.

    Parameters
    ~~~~~~~~~~
    :param a: The seed.
    :type a: int | float | str | bytes | bytearray | None
    :param version: The version to use.
    :type version: Literal[1, 2]

    Example Usage
    ~~~~~~~~~~~~~
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
    """

    orig_state = getstate()
    rand_seed(a, version)

    try:
        yield
    finally:
        setstate(orig_state)


@contextmanager
def tempdir():
    """
    tempdir
    -------
    Context manager that creates a temporary directory, deleting it on exit.

    Example Usage
    ~~~~~~~~~~~~~
    >>> with tempdir() as td:
    ...     print(td)
    ...
    'C:\\Users\\user\\AppData\\Local\\Temp\\tmpcnssgvv3'
    >>> # may vary depending on OS or machine setup
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
    --------
    Context manager that creates a temporary file, deleting it upon exit.

    Example Usage
    ~~~~~~~~~~~~~
    >>> with tempfile() as tf:
    ...     print(tf)
    ...
    'C:\\Users\\user\\AppData\\Local\\Temp\\tmp_fmy_5nk'
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
    ----------
    Context manager that temporarily changes the current working directory.

    Parameters
    ~~~~~~~~~~
    :param path: The new working directory path.
    :type path: str

    Raises
    ~~~~~~
    :raises TypeError: If path is not a str.

    Example Usage
    ~~~~~~~~~~~~~
    >>> from os import getcwd
    >>>
    >>> with change_dir("C:/Users/users/Desktop"):
    ...     print(getcwd())
    ...
    'C:\\Users\\users\\Desktop'
    >>>
    >>> getcwd()
    'C:\\Users\\users\\Desktop\\Programming\\Python\\devgizmos'
    """

    ensure_instance_of(path, str)

    orig_dir = getcwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(orig_dir)


@contextmanager
def change_env(**env_vars):
    """
    change_env
    ----------
    Context manager that temporarily sets environment variables.

    Parameters
    ~~~~~~~~~~
    :param env_vars: The environment variables to set.
    :type env_vars: str

    Raises
    ~~~~~~
    :raises TypeError: If any env var in env_vars is not a str.

    Example Usage
    ~~~~~~~~~~~~~
    >>> from os import environ
    >>>
    >>> with change_env(PATH="/tmp"):
    ...     print(environ["PATH"])
    ...
    /tmp
    >>>
    >>> print(environ["PATH"])
    'C:\\Previous\\Path1;C:\\Previous\\Path2'
    >>> # etc
    """

    for var in env_vars.values():
        ensure_instance_of(var, str)

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
    --------
    Context manager that suppresses specified exceptions depending on the user.

    Parameters
    ~~~~~~~~~~
    :param exceptions: The exceptions provided to be suppress.
    :type exceptions: Type[BaseException]

    Example Usage
    ~~~~~~~~~~~~~
    >>> with suppress(FileNotFoundError):
    ...     open("example_file.txt")
    ...
    >>>
    (No traceback, exception suppressed)
    """

    ensure_superclass_of(BaseException, exceptions)

    try:
        yield
    except exceptions:
        pass


@contextmanager
def retry_on(exc, /, *, max_attempts=3, delay=1, backoff_strategy=None):
    """
    retry_on
    --------
    Context manager that retries a section of code if a specific exception is raised.

    Parameters
    ~~~~~~~~~~
    :param exc: The exception to retry on.
    :type exc: Type[BaseException]
    :param max_attempts: The maximum number of times to attempt to run the code, defaults to 3.
    :type max_attempts: int, optional
    :param delay: The starting delay in seconds, defaults to 1.
    :type delay: int, optional
    :param backoff_strategy: A function to determine the delay after each attempt, or None for no strategy.
    - The function should take delay as the first argument, and the attempt number as the second argument.
    - The function should return an int or float for the new delay time.
    - The delay will be updated BEFORE sleeping during each attempt loop.\n
    :type backoff_strategy: Callable[[int | float, int], int | float], optional

    Example Usage
    ~~~~~~~~~~~~~
    >>> from random import random
    >>>
    >>> def risky():
    ...     if random() > 0.5:
    ...             raise TypeError
    ...     else:
    ...             return 1
    ...
    >>>
    >>> with retry_on(TypeError):
    ...     risky()
    ...
    1
    """

    # type checks
    ensure_superclass_of(BaseException, exc)
    ensure_instance_of(max_attempts, int)
    ensure_instance_of(delay, (int, float))
    if backoff_strategy is not None:
        ensure_callable(backoff_strategy)

    # value checks
    ensure_in_bounds(max_attempts, 1, None)
    ensure_in_bounds(delay, 0, None, inclusive=False)

    attempt = 1
    while attempt <= max_attempts:
        try:
            yield
            break

        except exc:
            if attempt == max_attempts:
                raise

            if backoff_strategy is not None:
                delay = backoff_strategy(delay, attempt)
            sleep(delay)


@contextmanager
def profile(output_file=None):
    """
    profile
    =======
    Context manager used to measure and analyze the performance of a block of code.

    Parameters
    ~~~~~~~~~~
    :param output_file: The file to save the profile data to, defaults to None.
    :type output_file: str, optional

    Example Usage
    ~~~~~~~~~~~~~
    >>> with profile() as prof:
    ...     for i in range(1_000_000_000):
    ...         pass
    ...
    >>> prof.print_stats()
            13 function calls in 0.000 seconds

    Ordered by: standard name

    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
         1    0.000    0.000    0.000    0.000 <stdin>:1(<module>)
       ...      ...      ...      ...      ... ...


    >>>
    >>> # saving to a file:
    >>> with profile("profile_output.prof"):
    ...     for i in range(1_000_000_000):
    ...         pass
    ...
    >>> # Load and analyze a saved profile:
    >>> import pstats
    >>> stats = pstats.Stats("profile_output.prof")
    >>> stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
    """

    prof = cProfile.Profile()
    prof.enable()

    try:
        yield prof
    finally:
        # if not output_file:
        # s = StringIO()
        # ps = pstats.Stats(prof, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
        # ps.print_stats()
        # print(s.getvalue())

        if output_file:
            prof.dump_stats(output_file)


@contextmanager
def future_manager(future):
    """
    future_manager
    ==============
    Context Manager that ensures that a future is cancelled properly.

    Parameters
    ~~~~~~~~~~
    :param future: The future that is being managed.
    :type future: concurrent.futures.Future

    Example Usage
    ~~~~~~~~~~~~~
    >>> from concurrent.futures import Future
    >>> some_future: Future = Future()
    ...
    >>> with future_manager(some_future):
    ...     print("Future is being managed")
    ...
    >>> print(some_future.cancelled)
    Future is being managed
    True
    """
    ensure_instance_of(future, Future)

    try:
        yield
    finally:
        future.cancel()
