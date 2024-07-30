# pylint: disable=all

from contextlib import contextmanager
from datetime import datetime
from types import TracebackType
from typing import (
    Any,
    Callable,
    ContextManager,
    List,
    NoReturn,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
    Union,
)

F = TypeVar("F", bound=Callable[..., Any])

class _ExcData:
    """Helper class for returning caught exception data with FailureManager."""

    def __init__(
        self,
        type_: Type[BaseException],
        value: BaseException,
        traceback: TracebackType,
        time: datetime,
    ) -> None: ...
    @property
    def type(self) -> Type[BaseException]: ...
    @property
    def value(self) -> BaseException: ...
    @property
    def traceback(self) -> TracebackType: ...
    @property
    def time(self) -> datetime: ...
    def reraise(self) -> NoReturn: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Retry:
    def __init__(
        self,
        max_attempts: Optional[int],
        delay: Union[int, float],
        backoff_strategy: Optional[
            Callable[[Union[int, float], int], Union[int, float]]
        ] = None,
        exceptions: Tuple[Type[BaseException]] = (Exception,),
        raise_last: bool = False,
    ): ...
    def __call__(self, func: F, /) -> F: ...
    def on_retry(
        self, func: Optional[Callable[[int, BaseException], None]], /
    ) -> None: ...
    @property
    def max_attempts(self) -> int: ...
    @max_attempts.setter
    def max_attempts(self, m: int, /) -> None: ...
    @property
    def delay(self) -> Union[int, float]: ...
    @delay.setter
    def delay(self, d: Union[int, float], /) -> None: ...
    @property
    def backoff_strategy(
        self,
    ) -> Union[Callable[[Union[int, float], int], Union[int, float]], None]: ...
    @backoff_strategy.setter
    def backoff_strategy(
        self, bs: Optional[Callable[[Union[int, float], int], Union[int, float]]], /
    ) -> None: ...
    @property
    def exceptions(self) -> Tuple[Type[BaseException], ...]: ...
    @exceptions.setter
    def exceptions(self, excs: Tuple[Type[BaseException], ...], /) -> None: ...
    @property
    def raise_last(self) -> bool: ...
    @raise_last.setter
    def raise_last(self, rl: bool, /) -> None: ...
    @property
    def attempts(self) -> int: ...
    @property
    def suppressed(self) -> List[_ExcData]: ...
    def clear_suppressed(self) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
