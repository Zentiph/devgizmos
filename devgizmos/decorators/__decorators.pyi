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

from ..types import Decorator, Num

T = TypeVar("T")  # generic type
C = TypeVar("C")  # generic class instance type
F = TypeVar("F", bound=Callable[..., Any])

LoggingLevel = int

DecoratedFunc = Decorator
DecoratedCls = Callable[[Type], Type]

BackoffFunc = Callable[[Num, int], Num]

# base class to enforce type hints for lazy_property decorator
class SupportsLazyProperty(Protocol):
    pass

class UnsupportedOSError(Exception): ...
class ConditionError(Exception): ...

def retry(
    max_attempts: int,
    delay: Num,
    backoff_strategy: Optional[BackoffFunc] = None,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    raise_last: bool = True,
    *,
    success_fmt: Optional[str] = "",
    failure_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def async_retry(
    max_attempts: int,
    delay: Num,
    backoff_strategy: Optional[BackoffFunc] = None,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    raise_last: bool = True,
    *,
    success_fmt: Optional[str] = "",
    failure_fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def timeout(
    cutoff: Num,
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
    *exceptions: Type[BaseException],
    fmt: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> DecoratedFunc: ...
def conditional(
    condition: Callable[..., bool], *, raise_exc: bool = False
) -> DecoratedFunc: ...
@overload
def rate_limit(interval: Num) -> DecoratedFunc: ...
@overload
def rate_limit(calls: int, period: Num) -> DecoratedFunc: ...
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

class PeriodicTask:
    def __init__(
        self,
        interval: Union[int, float],
        func: F,
        *args: Tuple[Any, ...],
        **kwargs: Any,
    ) -> None: ...
    def _target(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

def periodic_running_task(interval: Union[int, float]) -> DecoratedFunc: ...
