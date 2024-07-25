# pylint: disable=all

from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def tracer(
    *,
    entry_fmt: Optional[str] = "",
    exit_fmt: Optional[str] = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
