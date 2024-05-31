# pylint: disable=all

from typing import Any, Callable


def timer(
    unit: str = "ns",
    precision: int = 0,
    *,
    msg_format: str = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
