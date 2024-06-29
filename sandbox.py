# pylint: disable=all

from random import random
from time import perf_counter, sleep

import devgizmos as dgiz
import devgizmos.checks as cks
import devgizmos.decorators as decs

logger = dgiz.BasicLogger()


@decs.tracer(entry_fmt=None, exit_fmt=None)
def test(*args):
    return all(args)


test()
