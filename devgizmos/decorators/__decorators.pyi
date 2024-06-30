# pylint: disable=all

# import all of logging to explicitly show in type hints
# that INFO, WARNING, ERROR, and Logger are from logging
import logging
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from ..types import Decorator, Number

T = TypeVar("T")  # generic type
C = TypeVar("C")  # generic class instance type

LoggingLevel = int

DecoratedFunc = Decorator
DecoratedCls = Callable[[Type], Type]

BackoffFunc = Callable[[Number, int], Number]

# base class to enforce type hints for lazy_property decorator
class SupportsLazyProperty(Protocol):
    pass

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
def timer_rs(
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
) -> DecoratedFunc: ...
def benchmark(
    trials: int = 10,
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    *,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def benchmark_rs(
    trials: int = 10, unit: Literal["ns", "us", "ms", "s"] = "ns", precision: int = 3
) -> DecoratedFunc: ...
def retry(
    max_attempts: int,
    delay: Number,
    backoff_strategy: Optional[BackoffFunc] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    *,
    success_fmt: Optional[str] = "",
    failure_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def async_retry(
    max_attempts: int,
    delay: Number,
    backoff_strategy: Optional[BackoffFunc] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    *,
    success_fmt: Optional[str] = "",
    failure_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def timeout(
    cutoff: Number,
    *,
    success_fmt: Optional[str] = "",
    failure_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    success_level: LoggingLevel = logging.INFO,
    failure_level: LoggingLevel = logging.WARNING,
) -> DecoratedFunc: ...
def fallback(
    fallback_func: Callable[..., Any], *args: Any, **kwargs: Any
) -> DecoratedFunc: ...
def tracer(
    *,
    entry_fmt: Optional[str] = "",
    exit_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def error_logger(
    suppress: bool = True,
    *,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.ERROR,
) -> DecoratedFunc: ...
def suppressor(
    *exceptions: Type[Exception],
    fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def conditional(
    condition: Callable[..., bool], *, raise_exc: bool = False
) -> DecoratedFunc: ...
@overload
def rate_limit(interval: Number) -> DecoratedFunc: ...
@overload
def rate_limit(calls: int, period: Number) -> DecoratedFunc: ...
@overload
def cache(*, type_specific: bool = False) -> DecoratedFunc: ...
@overload
def cache(maxsize: int, *, type_specific: bool = False) -> DecoratedFunc: ...

class lazy_property(Generic[C, T]):
    def __init__(self, func: Callable[[C], T]) -> None: ...
    def __get__(self, instance: C, owner: Any) -> T: ...

def deprecated(
    reason: str,
    version: Optional[Union[int, float, str]] = None,
    date: Optional[str] = None,
) -> DecoratedFunc: ...
def decorate_all_methods(
    decorator: Decorator, *args: Any, **kwargs: Any
) -> DecoratedCls: ...
def immutable(cls: Type[T]) -> DecoratedCls: ...
def singleton() -> DecoratedCls: ...
def type_checker() -> DecoratedFunc: ...
