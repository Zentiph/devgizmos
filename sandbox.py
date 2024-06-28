# pylint: disable=all

from random import random
from time import perf_counter, sleep

import devgizmos as dgiz
import devgizmos.checks as cks
import devgizmos.decorators as decs

logger = dgiz.BasicLogger()

cks.check_in_range(10, range(0, 4))
