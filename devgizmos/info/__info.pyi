# pylint: disable=all

from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def tracer(
    *,
    entry_msg: Optional[str] = "",
    exit_msg: Optional[str] = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
