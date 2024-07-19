# pylint: disable=all

from types import TracebackType
from typing import Any, Callable, Optional, Type, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])

class Timeout:
    def __init__(
        self,
        cutoff: Union[int, float],
        exc: Optional[Type[BaseException]] = TimeoutError,
    ) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def __call__(self, func: F, /) -> F: ...
    def __unix_enter(self) -> None: ...
    def __unix_exit(self) -> None: ...
    def __windows_enter(self) -> None: ...
