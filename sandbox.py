# pylint: disable=all

from random import random
from time import perf_counter, sleep

import devgizmos as dgiz
import devgizmos.decorators as decs

logger = dgiz.BasicLogger()

"""
@decs.timer(logger=logger)
def wait(t, /):
    sleep(t)


wait(2)
"""

"""
@decs.benchmark(unit="s")
def wait(t, /):
    sleep(t)


wait(0.4)
"""

"""
@decs.retry(backoff_factor=3, logger=logger)
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

"""
@decs.decorate_all_methods(decs.timer, logger=logger)
class TestClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def wait(self, t, /):
        sleep(t + self.a + self.b)


tc = TestClass(1, -1)
tc.wait(1)
"""

"""
@decs.cache(maxsize=2)
def expensive_operation(arg):
    # expensive operation here
    sleep(arg)
    return random()


print(expensive_operation(2))
print(expensive_operation(2))
print(expensive_operation(1))
print(expensive_operation(1))
print(expensive_operation(3))
print(expensive_operation(2))
"""

"""
@decs.rate_limit(1, 1)
def printer():
    print(f"Printing at time {perf_counter()}!")


printer()
printer()
printer()
"""

"""
@decs.suppress(Exception)
def risky():
    raise TypeError


risky()
"""
