# pylint: disable=all

import threading
from typing import (
    TypeVar,
    Callable,
    Any,
    Union,
    Tuple,
    Type,
    ContextManager,
    Iterable,
    List,
)

F = TypeVar("F", bound=Callable[..., Any])

Decorator = Callable[[F], F]

DecoratedFunc = Decorator
DecoratedCls = Callable[[Type], Type]

def thread_manager(
    target: Callable[..., Any], *args: Tuple[Any, ...], **kwargs: Any
) -> ContextManager[threading.Thread]: ...
def lock_handler(lock: threading.Lock) -> ContextManager[None]: ...
def barrier_sync(barrier: threading.Barrier) -> ContextManager[None]: ...

class PeriodicTask:
    def __init__(
        self,
        interval: Union[int, float],
        func: F,
        *args: Tuple[Any, ...],
        **kwargs: Any,
    ) -> None: ...
    def _target(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

def periodic_task(interval: Union[int, float]) -> DecoratedFunc: ...
def batch_processor(
    data: Iterable[Any], workers: int, process_function: F
) -> List[Any]: ...

class QueueProcessor:
    def __init__(self, workers: int, process_function: F) -> None: ...
    def _consumer(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def add_task(self, item: Any) -> None: ...
