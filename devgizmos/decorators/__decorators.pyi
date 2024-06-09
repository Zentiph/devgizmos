# pylint: disable=all

from typing import Any, Callable, Optional, Tuple, Type, Union

def timer(
    unit: str = "ns", precision: int = 0, *, msg_format: Optional[str] = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def retry(
    max_attempts: int = 3,
    delay: Union[int, float] = 1,
    *,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    raise_last: bool = True,
    success_msg_format: Optional[str] = "",
    failure_msg_format: Optional[str] = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def timeout(
    cutoff: Union[int, float],
    *,
    success_msg_format: Optional[str] = "",
    failure_msg_format: Optional[str] = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
