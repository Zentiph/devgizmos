# pylint: disable=all

from abc import ABC, abstractmethod
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
    Union,
)

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
    @property
    def cutoff(self) -> Union[int, float]: ...
    @property
    def exc(self) -> Type[BaseException]: ...
    @exc.setter
    def exc(self, e: Type[BaseException], /) -> None: ...

class FailureHandler(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None: ...
    @abstractmethod
    def __call__(self) -> None: ...
    @property
    def priority(self) -> int: ...
    @priority.setter
    def priority(self, p: int, /) -> None: ...
    @property
    def returned(self) -> Any: ...
    @abstractmethod
    def __str__(self) -> str: ...
    @abstractmethod
    def __repr__(self) -> str: ...

class Fallback(FailureHandler):
    def __init__(
        self, func: Callable[..., Any], *args: Any, **kwargs: Dict[str, Any]
    ) -> None: ...
    def __call__(self) -> None: ...
    def validate(self) -> Union[Type[Exception], None]: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class _HandlerCollection:
    def __init__(self, *handlers: Optional[FailureHandler]) -> None: ...
    @property
    def priorities(self) -> Tuple[int, ...]: ...
    def __iter__(self) -> Iterator: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> FailureHandler: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class FailureManager:
    def __init__(
        self,
        *handlers: Optional[FailureHandler],
        exceptions: Tuple[Type[BaseException]] = (Exception,),
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def __call__(self, func: F, /) -> F: ...
    def add_handler(self, handler: FailureHandler, /) -> None: ...
    def del_handler(self, priority: int, /) -> None: ...
    @property
    def handlers(self) -> _HandlerCollection: ...
    @property
    def exceptions(self) -> Tuple[Type[BaseException], ...]: ...
    @exceptions.setter
    def exceptions(self, excs: Tuple[Type[BaseException], ...]) -> None: ...
    @property
    def caught(self) -> Type[BaseException]: ...
