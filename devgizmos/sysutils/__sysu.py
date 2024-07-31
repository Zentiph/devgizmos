"""
sysutils.__sysu
===============
Module containing system related utility.
"""

from contextlib import contextmanager
from os import chdir, environ, getcwd, remove, rmdir
from tempfile import NamedTemporaryFile, mkdtemp

from ..errguards import ensure_instance_of


@contextmanager
def tempdir():
    """
    tempdir()
    ---------
    Context manager that creates a temporary directory, deleting it upon exit.

    Return
    ~~~~~~
    :yield: The temporary directory's path.
    :rtype: str

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
    tempfile()
    ----------
    Context manager that creates a temporary file, deleting it upon exit.

    Return
    ~~~~~~
    :yield: The temporary file's path.
    :rtype: str

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
    change_dir()
    ------------
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
    change_env()
    ------------
    Context manager that temporarily sets environment variables, reverting them upon exit.

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
