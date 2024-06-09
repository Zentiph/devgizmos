# pylint: disable=all

import devgizmos.decorators as decs
from time import sleep


@decs.timer()
@decs.timeout(2)
def process(i):
    for _ in range(i):
        pass


process(1)
process(1_000)
process(1_000_000)
process(1_000_000_000)
