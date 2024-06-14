# pylint: disable=all

import devgizmos as dgiz
import devgizmos.decorators as decs

from random import random
from time import sleep

logger = dgiz.BasicLogger()

"""
@decs.timer(logger=logger)
def wait(t, /):
    sleep(t)


wait(2)
"""

"""
@decs.retry(logger=logger)
def risky():
    if random() > 0.2:
        raise ZeroDivisionError


risky()
"""

"""
@decs.timeout(2, logger=logger)
def potentially_lengthy(iters=1_000_000_000):
    for _ in range(iters):
        pass


potentially_lengthy()
"""

"""
@decs.call_logger(logger=logger)
def foo(*args, **kwargs):
    return args, kwargs


foo(1, "Hello", kwarg1=5.5, kwarg2="Hi")
"""

"""
@decs.error_logger(logger=logger)
def raiser():
    raise ValueError("Uh oh")


raiser()
"""
