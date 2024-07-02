# pylint: disable=all

from contextlib import contextmanager
from typing import Iterator, Literal, Union

@contextmanager
def seed(
    a: Union[int, float, str, bytes, bytearray, None], version: Literal[1, 2] = 2
) -> Iterator[None]: ...
