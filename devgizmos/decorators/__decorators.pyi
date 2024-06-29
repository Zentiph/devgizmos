# pylint: disable=all

import logging
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
DecoratedFunc = Decorator
DecoratedCls = Callable[[Type], Type]
LoggingLevel = int

class UnsupportedOSError(Exception): ...
class ConditionError(Exception): ...

def timer(
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    *,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def benchmark(
    trials: int = 10,
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def retry(
    max_attempts: int,
    delay: Union[int, float],
    backoff_factor: Union[int, float] = 1,
    *,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    success_fmt: str = "",
    failure_fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def timeout(
    cutoff: Union[int, float],
    *,
    success_fmt: str = "",
    failure_fmt: str = "",
    logger: Optional[logging.Logger] = None,
    success_level: LoggingLevel = logging.INFO,
    failure_level: LoggingLevel = logging.WARNING,
) -> DecoratedFunc: ...
@overload
def cache(*, type_specific: bool = False) -> DecoratedFunc: ...
@overload
def cache(maxsize: int, *, type_specific: bool = False) -> DecoratedFunc: ...
def singleton() -> DecoratedCls: ...
def type_checker() -> DecoratedFunc: ...
def deprecated(
    reason: str,
    version: Optional[Union[int, float, str]] = None,
    date: Optional[str] = None,
) -> DecoratedFunc: ...
def tracer(
    entry_fmt: str = "",
    exit_fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def error_logger(
    fmt: str = "",
    suppress: bool = True,
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.ERROR,
) -> DecoratedFunc: ...
def decorate_all_methods(
    decorator: Decorator, *args: Any, **kwargs: Any
) -> DecoratedCls: ...
@overload
def rate_limit(interval: Union[int, float]) -> DecoratedFunc: ...
@overload
def rate_limit(calls: int, period: Union[int, float]) -> DecoratedFunc: ...
def suppress(
    *exceptions: Type[Exception],
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def conditional(
    condition: Callable[..., bool], *, raise_exc: bool = False
) -> DecoratedFunc: ...
