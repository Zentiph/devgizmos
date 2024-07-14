# pylint: disable=all

import logging
from types import TracebackType
from typing import Literal, Optional, Self, Type, Union

from ..types import Decorator

LoggingLevel = int
DecoratedFunc = Decorator

class Timer:
    def __init__(
        self,
        unit: Literal["ns", "us", "ms", "s"] = "ns",
        precision: int = 3,
        *,
        fmt: str = "",
        logger: Optional[logging.Logger] = None,
        level: LoggingLevel = logging.INFO,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def elapsed(self) -> float: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...

def dectimer(
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    *,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
