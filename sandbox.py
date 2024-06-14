# pylint: disable=all

import devgizmos as dgiz
import devgizmos.decorators as decs

import logging
from time import sleep

logger = dgiz.BasicLogger()


@decs.timer(logger=logger)
def wait(t, /):
    sleep(t)


wait(2)
