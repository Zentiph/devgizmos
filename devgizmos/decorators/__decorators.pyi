# pylint: disable=all

from logging import INFO, Logger
from typing import Any, Callable, Optional, Tuple, Type, Union

LoggingLevel = int | str

def timer(
    unit: str = "ns",
    precision: int = 0,
    *,
    msg_format: Optional[str] = "",
    logger: Optional[Logger] = None,
    level: LoggingLevel = INFO,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def retry(
    max_attempts: int = 3,
    delay: Union[int, float] = 1,
    *,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    success_msg_format: Optional[str] = "",
    failure_msg_format: Optional[str] = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def timeout(
    cutoff: Union[int, float],
    *,
    success_msg_format: Optional[str] = "",
    failure_msg_format: Optional[str] = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def cache() -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def singleton() -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def type_checker() -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def deprecated(reason: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def log_calls(
    logger: Union[Logger, None]
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
