"""
contmngrs.__contmngrs
=====================
Module containing context managers.
"""

from contextlib import contextmanager
from random import seed as rand_seed


@contextmanager
def seed(a, version=2):
    """
    seed
    ====
    Context manager that initializes the content within with the given seed.
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

    rand_seed(a, version)

    try:
        yield
    finally:
        rand_seed()
