# pylint: disable=all

from types import TracebackType
from typing import Any, Callable, Optional, Type, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])

class UnsupportedOSError(Exception): ...

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
    ) -> bool: ...
    def __call__(self, func: F, /) -> F: ...
    @property
    def cutoff(self) -> Union[int, float]: ...
    @property
    def exc(self) -> Type[BaseException]: ...
    @exc.setter
    def exc(self, e: Type[BaseException], /) -> None: ...
