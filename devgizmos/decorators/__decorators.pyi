# pylint: disable=all

from logging import ERROR, INFO, Logger, WARNING
from typing import Any, Callable, Literal, Optional, Tuple, Type, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
LoggingLevel = int | str

def timer(
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 0,
    *,
    fmt: str = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> Callable[[F], F]: ...
def retry(
    max_attempts: int = 3,
    delay: Union[int, float] = 1,
    *,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    success_fmt: str = "",
    failure_fmt: str = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> Callable[[F], F]: ...
def timeout(
    cutoff: Union[int, float],
    *,
    success_fmt: str = "",
    failure_fmt: str = "",
    logger: Optional[Logger] = None,
    success_level: LoggingLevel = INFO,
    failure_level: LoggingLevel = WARNING,
) -> Callable[[F], F]: ...
def cache(maxsize: Optional[int] = None) -> Callable[[F], F]: ...
def singleton() -> Callable[[F], F]: ...
def type_checker() -> Callable[[F], F]: ...
def deprecated(
    reason: str,
    version: Union[int, float, str, None] = None,
    date: Optional[str] = None,
) -> Callable[[F], F]: ...
def call_logger(
    fmt: str = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> Callable[[F], F]: ...
def error_logger(
    fmt: str = "",
    suppress: bool = True,
    logger: Optional[Logger] = None,
    level: LoggingLevel = ERROR,
) -> Callable[[F], F]: ...
def decorate_all_methods(
    decorator: Decorator, *dec_args: Any, **dec_kwargs: Any
) -> Type: ...
