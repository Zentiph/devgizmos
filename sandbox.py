# pylint: disable=all

import devgizmos as dgiz

from random import randint


@dgiz.decorators.retry()
def risky():
    if randint(1, 3) == 3:
        return None
    raise ValueError


risky()
