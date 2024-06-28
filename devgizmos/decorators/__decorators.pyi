# pylint: disable=all

from logging import ERROR, INFO, WARNING, Logger
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
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> DecoratedFunc: ...
def benchmark(
    trials: int = 10,
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    fmt: str = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
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
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> DecoratedFunc: ...
def timeout(
    cutoff: Union[int, float],
    *,
    success_fmt: str = "",
    failure_fmt: str = "",
    logger: Optional[Logger] = None,
    success_level: LoggingLevel = INFO,
    failure_level: LoggingLevel = WARNING,
) -> DecoratedFunc: ...
@overload
def cache() -> DecoratedFunc: ...
@overload
def cache(maxsize: int) -> DecoratedFunc: ...
def singleton() -> DecoratedCls: ...
def type_checker() -> DecoratedFunc: ...
def deprecated(
    reason: str,
    version: Union[int, float, str, None] = None,
    date: Optional[str] = None,
) -> DecoratedFunc: ...
def tracer(
    entry_fmt: str = "",
    exit_fmt: str = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> DecoratedFunc: ...
def error_logger(
    fmt: str = "",
    suppress: bool = True,
    logger: Optional[Logger] = None,
    level: LoggingLevel = ERROR,
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
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> DecoratedFunc: ...
def conditional(
    condition: Callable[..., bool], *, raise_exc: bool = False
) -> DecoratedFunc: ...
