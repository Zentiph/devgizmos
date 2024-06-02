# pylint: disable=all

import devgizmos as dgiz

from time import sleep


@dgiz.decorators.timer()
def wait(s):
    sleep(s)
    return f"{s}"


wait(2)
