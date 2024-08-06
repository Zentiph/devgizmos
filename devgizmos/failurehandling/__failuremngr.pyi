# pylint: disable=all

from abc import ABC, abstractmethod
from datetime import datetime
from types import TracebackType
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Literal,
    NoReturn,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
    Union,
)

F = TypeVar("F", bound=Callable[..., Any])

class _FailureHandler(ABC):
    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @abstractmethod
    def __call__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    @property
    def activated(self) -> bool: ...
    @activated.setter
    def activated(self, a: bool, /) -> None: ...
    @property
    def priority(self) -> int: ...
    @priority.setter
    def priority(self, p: int, /) -> None: ...
    @property
    def returned(self) -> Any: ...
    @classmethod
    def with_priority(
        cls, priority: int, *args: Any, **kwargs: Any
    ) -> _FailureHandler: ...
    @abstractmethod
    def __str__(self) -> str: ...
    @abstractmethod
    def __repr__(self) -> str: ...

class Suppress(_FailureHandler):
    def __init__(self) -> None: ...
    def __call__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Fallback(_FailureHandler):
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None: ...
    def __call__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def validate(self) -> bool: ...
    def error_scan(self) -> Union[Type[Exception], None]: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class DifferentException(_FailureHandler):
    def __init__(
        self, exc: Union[Type[BaseException], str], fmt: str = "{value}"
    ) -> None: ...
    def __call__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class _HandlerCollection:
    def __init__(self, *handlers: Optional[_FailureHandler]) -> None: ...
    @property
    def priorities(self) -> Tuple[int, ...]: ...
    def __iter__(self) -> Iterator: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> _FailureHandler: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class _ExcData:
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

class FailureManager:
    def __init__(
        self,
        *handlers: Optional[_FailureHandler],
        exceptions: Tuple[Type[BaseException]] = (Exception,),
        assign_priorities: bool = True,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool: ...
    def __call__(self, func: F, /) -> F: ...
    def sort_handler_priorities(self) -> None: ...
    def set_priority(self, handler: _FailureHandler, priority: int, /) -> None: ...
    def add_handler(self, handler: _FailureHandler, /) -> None: ...
    def del_handler(self, priority: int, /) -> None: ...
    @property
    def handlers(self) -> _HandlerCollection: ...
    @property
    def exceptions(self) -> Tuple[Type[BaseException], ...]: ...
    @exceptions.setter
    def exceptions(self, excs: Tuple[Type[BaseException], ...]) -> None: ...
    @property
    def caught(
        self,
    ) -> List[_ExcData]: ...