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
