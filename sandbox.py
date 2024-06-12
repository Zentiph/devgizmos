# pylint: disable=all

import devgizmos.decorators as decs

from time import sleep


@decs.retry(success_msg_format="{args} {kwargs} {returned}")
def foo():
    sleep(1)


foo()
